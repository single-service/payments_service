from django.db import models
from django.utils.translation import gettext as _

from applications.models import AbstractBaseModel
from applications.choices import PaymentSystemsChoices

from .choices import CurrencyChoices


class Order(AbstractBaseModel):
    # Relations
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE)
    payment_item = models.ForeignKey("payments.PaymentItem", on_delete=models.SET_NULL, null=True, blank=True)

    # Fields
    payment_system = models.IntegerField(_("Payment System"), choices=PaymentSystemsChoices.choices)
    payment_dt = models.DateTimeField(_("Payment Datetime"), null=True, blank=True)
    status = models.IntegerField(_("Status"), choices=CurrencyChoices.choices, default=CurrencyChoices.CREATED)
    name = models.CharField(_("Name"), max_length=100)
    price = models.DecimalField(_("Price"), max_digits=11, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, choices=CurrencyChoices.choices)
    is_subscription = models.BooleanField()
    items_count = models.PositiveIntegerField(_("Items Count"), default=1)
    discount_value = models.PositiveIntegerField(_("Discount Value, %"), null=True, blank=True)
    refunding_start_dt = models.DateTimeField(_("Refunding Request Datetime"), null=True, blank=True)
    refund_dt = models.DateTimeField(_("Refund Datetime"), null=True, blank=True)
    refund_amount = models.DecimalField(_("Refund Amount"), max_digits=11, decimal_places=2, null=True, blank=True)
    fee = models.DecimalField(_("Fee"), max_digits=11, decimal_places=2, null=True, blank=True)
    receipt_link = models.URLField(_("Receipt Url"), null=True, blank=True)

    class Meta:
        verbose_name = _("Order")
        verbose_name_plural = _("Orders")
