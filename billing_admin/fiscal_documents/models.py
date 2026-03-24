from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

from applications.models import AbstractBaseModel


class FiscalDocument(AbstractBaseModel):

    class Status(models.TextChoices):
        DONE = "done", "Done"
        FAIL = "fail", "Fail"
        WAIT = "wait", "Wait"

    class DocumentType(models.TextChoices):
        SALE = "sale", "Продажа"
        REFUND = "refund", "Возврат"

    order = models.ForeignKey(
        "billing.Order",
        on_delete=models.CASCADE,
        related_name="fiscal_documents",
        verbose_name=_("Заказ"),
        blank=True,
        null=True
    )
    refund = models.ForeignKey(
        "refunds.Refund",
        on_delete=models.CASCADE,
        related_name="fiscal_documents",
        verbose_name=_("Возврат"),
        blank=True,
        null=True
    )
    ofd_document_id = models.UUIDField(
        _("Идентификатор документа в ОФД"),
        blank=True,
        null=True
    )
    ofd_document_url = models.URLField(
        _("Ссылка на документ из ОФД"),
        blank=True,
        null=True
    )
    status = models.CharField(
        _("Статус документа"),
        max_length=10,
        choices=Status.choices,
        blank=True,
        null=True
    )
    error = models.JSONField(
        _("Ошибка"),
        blank=True,
        null=True
    )
    request_payload = models.JSONField(
        _("Сформированные клиентом данные для запроса ЭФД в ОФД"),
    )
    document_type = models.CharField(
        _("Тип документа"),
        max_length=10,
        choices=DocumentType.choices
    )

    class Meta:
        db_table = "fiscal_documents"
        verbose_name = "Фискальный документ"
        verbose_name_plural = "Фискальные документы"

    def __str__(self):
        if self.order:
            base = self.order.name
        elif self.refund:
            base = f"Refund {self.refund.id}"
        else:
            base = "Unknown"
        return f"{base}/{self.get_document_type_display()} ({self.status})"
    
    def clean(self):
        if self.document_type == self.DocumentType.SALE and not self.order:
            raise ValidationError("SALE document must have order")

        if self.document_type == self.DocumentType.REFUND and not self.refund:
            raise ValidationError("REFUND document must have refund")

        if self.order and self.refund:
            raise ValidationError("Document cannot have both order and refund")
