import uuid

from django.db import models
from django.utils.translation import gettext as _

from .choices import OFDInterfaceChoices, PaymentSystemsChoices, SnoChoices, TaxChoices


class AbstractBaseModel(models.Model):
    # Fields
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=100, db_index=True)
    created_dt = models.DateTimeField(_('Date of creation'), auto_now_add=True, editable=False)
    updated_dt = models.DateTimeField(_('Date of update'), auto_now=True, editable=True)

    class Meta:
        abstract = True


class Application(AbstractBaseModel):
    name = models.CharField(_("Name"), max_length=200)
    payment_system = models.IntegerField(_("Payment System"), choices=PaymentSystemsChoices.choices)
    callback_url = models.URLField(_("Callback Url"), null=True, blank=True, default=None)
    is_fiscalisation = models.BooleanField(_("Is Fiscalization"), default=False)
    sno = models.IntegerField(
        _("Налогоблажение(Если включена фискализация)"),
        choices=SnoChoices.choices,
        null=True,
        default=None
    )
    tax = models.IntegerField(
        _("НДС(Если налогоблажение Общая СН)"),
        choices=TaxChoices.choices,
        null=True,
        default=TaxChoices.NO_NDS
    )
    email = models.EmailField(_("Электронная почта организации"), blank=True)
    inn = models.CharField(_("ИНН организации"), blank=True, max_length=12)
    payment_address = models.CharField(_("Место расчетов"), blank=True, max_length=255)
    ofd_interface = models.IntegerField(
        _("OFD interface"), 
        choices=OFDInterfaceChoices.choices, 
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Application")
        verbose_name_plural = _("Applications")

    def __str__(self):
        return self.name


class ApplicationToken(AbstractBaseModel):
    # Relations
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE)

    # Fields
    token = models.CharField(_("Token"), max_length=200)
    salt = models.CharField(_("Salt"), max_length=10)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = _("Application Token")
        verbose_name_plural = _("Application Tokens")

    def __str__(self):
        return self.token


class PaymentSystemParamter(AbstractBaseModel):
    # Relations
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE)

    # Fields
    name = models.CharField(_("Name"), max_length=200)
    parameter_value = models.CharField(_("Parameter Value"), max_length=200, null=True, blank=True)
    payment_system = models.IntegerField(_("Payment System"), choices=PaymentSystemsChoices.choices)

    class Meta:
        verbose_name = _("Payment System Paramter")
        verbose_name_plural = _("Payment System Paramtres")

    def __str__(self):
        return self.name


class OFDInterfaceParamter(AbstractBaseModel):
    # Relations
    application = models.ForeignKey("applications.Application", on_delete=models.CASCADE)

    # Fields
    name = models.CharField(_("Name"), max_length=200)
    parameter_value = models.CharField(_("Parameter Value"), max_length=200, null=True, blank=True)
    ofd_interface = models.IntegerField(_("OFD Interface"), choices=OFDInterfaceChoices.choices)

    class Meta:
        verbose_name = _("OFD Interface Paramter")
        verbose_name_plural = _("OFD Interface Paramter")

    def __str__(self):
        return self.name
