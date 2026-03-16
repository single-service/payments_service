from django.db import models
from django.utils.translation import gettext as _

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
        verbose_name=_("Заказ")
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
        return f"{self.order.name}/{self.get_document_type_display()} ({self.status})"
