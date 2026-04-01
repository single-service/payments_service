import os
import uuid
from datetime import datetime

import requests
from applications.models import OFDInterfaceParamter
from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import gettext as _
from fiscal_documents.models import FiscalDocument
from unfold.admin import ModelAdmin, TabularInline

from .models import Expense, Order

SNO_MAP = {
    1: "osn",
    2: "usn_income",
    3: "usn_income_outcome",
    4: "esn",
    5: "patent"
}

ATOL_BASE_URL = "https://online.atol.ru/possystem/v5"


def _get_atol_token(login, password):
    resp = requests.post(
        f"{ATOL_BASE_URL}/getToken",
        json={"login": login, "pass": password},
        timeout=30,
    )
    data = resp.json()
    return data.get("token")


def _send_fiscal_check(order):
    application = order.application
    params = {
        p.name: p.parameter_value
        for p in OFDInterfaceParamter.objects.filter(application=application)
    }
    login = params.get("ATOL_LOGIN")
    password = params.get("ATOL_PASSWORD")
    group_id = params.get("ATOL_ID_GROUP_KKT")

    if not all([login, password, group_id]):
        return False, "Не заполнены параметры АТОЛ (ATOL_LOGIN, ATOL_PASSWORD, ATOL_ID_GROUP_KKT)"

    token = _get_atol_token(login, password)
    if not token:
        return False, "Не удалось получить токен АТОЛ"

    nomenclature = order.nomenclature or []
    total = 0
    items = []
    for entity in nomenclature:
        price_rubles = entity.get("price", 0) / 100
        count = entity.get("count", 1)
        amount_kopecks = entity.get("amount")
        amount_rubles = (amount_kopecks / 100) if amount_kopecks is not None else round(price_rubles * count, 2)
        total += amount_rubles
        position = {
            "name": entity.get("name"),
            "quantity": count,
            "price": price_rubles,
            "sum": amount_rubles,
            "vat": {"type": entity.get("nds")},
        }
        if entity.get("payment_method"):
            position["payment_method"] = entity["payment_method"]
        if entity.get("payment_type"):
            position["payment_object"] = entity["payment_type"]
        if entity.get("measure") is not None:
            position["measure"] = entity["measure"]
        items.append(position)

    SITE_HOST = os.getenv("SITE_HOST", "")
    external_id = str(uuid.uuid4())
    data = {
        "receipt": {
            "items": items,
            "client": {"email": order.user_email},
            "company": {
                "inn": application.inn,
                "sno": SNO_MAP.get(application.sno),
                "email": application.email,
                "payment_address": application.payment_address,
            },
            "payments": [{"type": 1, "sum": total}],
            "total": total,
        },
        "service": {
            "callback_url": f"https://{SITE_HOST}/api/v1/callback-atol/" if SITE_HOST else ""
        },
        "timestamp": datetime.now().strftime("%d.%m.%Y %H:%M:%S"),
        "external_id": external_id,
    }

    if order.additional_data and isinstance(order.additional_data, dict):
        name = order.additional_data.get("name", "")
        value = order.additional_data.get("value", "")
        if name and value:
            data["receipt"]["additional_user_props"] = {
                "name": str(name)[:64],
                "value": str(value)[:256],
            }

    resp = requests.post(
        f"{ATOL_BASE_URL}/{group_id}/sell",
        json=data,
        headers={"Token": token, "Content-Type": "application/json"},
        timeout=30,
    )

    FiscalDocument.objects.create(
        id=external_id,
        order=order,
        document_type=FiscalDocument.DocumentType.SALE,
        request_payload=data,
        status=FiscalDocument.Status.WAIT,
    )

    if resp.status_code not in (200, 201):
        return False, f"АТОЛ вернул ошибку: {resp.status_code} {resp.text[:200]}"

    return True, "Чек успешно отправлен в АТОЛ"


class FiscalDocumentInline(TabularInline):
    model = FiscalDocument
    extra = 0
    readonly_fields = ["created_dt", "document_type", "status", "fiscal_link", "error"]
    fields = ["created_dt", "document_type", "status", "fiscal_link", "error"]
    can_delete = False
    show_change_link = True

    def fiscal_link(self, obj):
        if obj.pk:
            url = reverse("admin:fiscal_documents_fiscaldocument_change", args=[obj.pk])
            return format_html('<a href="{}">Открыть чек</a>', url)
        return "-"
    fiscal_link.short_description = "Чек"


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = [
        "created_dt", "application", "status", "final_price", "currency", "is_subscription",
        "items_count", "discount_value", "payment_dt", "fee",
    ]
    ordering = ('-created_dt',)
    inlines = [FiscalDocumentInline]
    actions = ["send_fiscal_check"]

    @admin.action(description=_("Сформировать фискальный чек (АТОЛ)"))
    def send_fiscal_check(self, request, queryset):
        from .choices import StatusChoices
        for order in queryset:
            if order.status != StatusChoices.PAID:
                self.message_user(
                    request,
                    _(f"Заказ {order.id}: статус не 'Оплачен', пропущен"),
                    messages.WARNING,
                )
                continue
            if not order.application.is_fiscalisation:
                self.message_user(
                    request,
                    _(f"Заказ {order.id}: фискализация отключена для приложения"),
                    messages.WARNING,
                )
                continue
            ok, msg = _send_fiscal_check(order)
            level = messages.SUCCESS if ok else messages.ERROR
            self.message_user(request, _(f"Заказ {order.id}: {msg}"), level)


@admin.register(Expense)
class ExpenseAdmin(ModelAdmin):
    list_display = ["name", "expense_date", "amount",]
