from django.db import models
from django.utils.translation import gettext as _

from applications.models import AbstractBaseModel
from applications.choices import PaymentSystemsChoices

from payments.choices import CurrencyChoices
from .choices import StatusChoices


class Order(AbstractBaseModel):
    # Relations
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE)
    payment_item = models.ForeignKey("payments.PaymentItem", on_delete=models.SET_NULL, null=True, blank=True)

    # Fields
    payment_system = models.IntegerField(_("Payment System"), choices=PaymentSystemsChoices.choices)
    payment_dt = models.DateTimeField(_("Payment Datetime"), null=True, blank=True)
    status = models.IntegerField(_("Status"), choices=StatusChoices.choices, default=StatusChoices.CREATED)
    name = models.CharField(_("Name"), max_length=100)
    price = models.DecimalField(_("Price"), max_digits=11, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, choices=CurrencyChoices.choices)
    is_subscription = models.BooleanField()
    items_count = models.PositiveIntegerField(_("Items Count"), default=1)
    discount_value = models.PositiveIntegerField(_("Discount Value, %"), null=True, blank=True)
    # refunding_start_dt = models.DateTimeField(_("Refunding Request Datetime"), null=True, blank=True)
    # refund_dt = models.DateTimeField(_("Refund Datetime"), null=True, blank=True)
    # refund_amount = models.DecimalField(_("Refund Amount"), max_digits=11, decimal_places=2, null=True, blank=True)
    fee = models.DecimalField(_("Fee"), max_digits=11, decimal_places=2, null=True, blank=True)
    receipt_link = models.URLField(_("Receipt Url"), null=True, blank=True)
    user_id = models.CharField("User Id", max_length=300, default="")
    user_email = models.CharField("User Id", max_length=300, null=True, blank=True)
    idempotent_key = models.CharField("Idempotent Key", max_length=300, default="")
    amount = models.DecimalField(_("Real Amount"), max_digits=11, decimal_places=2, null=True, blank=True)
    discount_amount = models.DecimalField(_("Discount Amount"), max_digits=11, decimal_places=2, null=True, blank=True)
    final_price = models.DecimalField(_("Final Price"), max_digits=11, decimal_places=2, null=True, blank=True)
    payment_system_order_id = models.CharField(_("Order Id In Pay System"), max_length=300, default=None, null=True, blank=True)
    payment_link = models.TextField(_("Payment Link"), default="")
    is_subscription_first_order = models.BooleanField(_("First subscription order"), default=None, null=True, blank=True)
    invoice_id = models.TextField(_("Invoice Id"), default=None, null=True, blank=True)
    crc = models.TextField(_("CRC"), default=None, null=True, blank=True)
    nomenclature = models.JSONField(_("Nomenclature"), blank=True, default=None, null=True)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
