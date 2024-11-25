from django.db import models
from django.utils.translation import gettext as _

from applications.models import AbstractBaseModel

from .choices import CurrencyChoices


class PaymentItemsGroup(AbstractBaseModel):
    # Relations
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE)

    name = models.CharField(_("Name"), max_length=100)

    class Meta:
        verbose_name = _("Payment Items Group")
        verbose_name_plural = _("Payment Items Group")

    def __str__(self):
        return self.name


class PaymentItem(AbstractBaseModel):
    # Relations
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE)
    group = models.ForeignKey("payments.PaymentItemsGroup", on_delete=models.CASCADE)

    # Fields
    name = models.CharField(_("Name"), max_length=100)
    description = models.TextField(_("Description"), null=True, blank=True)
    price = models.DecimalField(_("Price"), max_digits=11, decimal_places=2)
    currency = models.CharField(_("Currency"), max_length=3, choices=CurrencyChoices.choices)
    is_subscription = models.BooleanField()

    class Meta:
        verbose_name = _("Payment Item")
        verbose_name_plural = _("Payment Items")

    def __str__(self):
        return self.name

class PaymentItemDiscount(AbstractBaseModel):
    # Relations
    payment_item = models.ForeignKey("payments.PaymentItem", on_delete=models.CASCADE)

    # Fields
    items_count = models.PositiveIntegerField(_("Items Count"))
    discount_value = models.PositiveIntegerField(_("Discount Value, %"))

    class Meta:
        verbose_name = _("Payment Item Discount")
        verbose_name_plural = _("Payment Items Discounts")

    def __str__(self):
        return str(self.discount_value)
