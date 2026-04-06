from django.db import models
from django.utils.translation import gettext as _

from applications.models import AbstractBaseModel


class Refund(AbstractBaseModel):

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        DONE = "done", "Done"
        FAILED = "failed", "Failed"

    order = models.ForeignKey(
        "billing.Order",
        on_delete=models.CASCADE,
        related_name="refunds",
        verbose_name=_("Order")
    )
    transaction_id = models.CharField(
        _("Transaction ID"),
        max_length=50,
    )
    amount = models.DecimalField(
        _("Refund amount"),
        max_digits=11,
        decimal_places=2
    )
    status = models.CharField(
        _("Status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    nomenclature = models.JSONField(
        _("Nomenclature"),
        blank=True,
        default=None,
        null=True
    )
    additional_data = models.JSONField(
        _("Additional data"),
        blank=True,
        default=None,
        null=True
    )

    class Meta:
        db_table = "refunds"
        verbose_name = "возврат"
        verbose_name_plural = "Возвраты"

    def __str__(self):
        return f"Возврат {self.order.name}. Сумма: {self.amount}"
