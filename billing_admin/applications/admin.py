import hashlib
import random
import secrets
import string

from django.contrib import admin, messages
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, User
from django.utils.html import format_html
from django.utils.translation import gettext as _
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action

from .choices import PAYMENT_SYSTEM_PARAMETERS_MAP
from .models import Application, ApplicationToken, PaymentSystemParamter

admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass


class PaymentSystemParamterInline(TabularInline):
    model = PaymentSystemParamter


@admin.register(Application)
class ApplicationAdmin(ModelAdmin):
    actions = ['create_token']
    inlines = [PaymentSystemParamterInline]

    @admin.action(description=_('Create token'))
    def create_token(modeladmin, request, queryset):
        chars = string.ascii_lowercase + string.ascii_letters + string.digits
        for obj in queryset:
            salt = "".join([random.choice(chars) for _ in range(8)])
            while True:
                real_token = "".join(secrets.choice(chars) for _ in range(16))
                full_token = f"{real_token}.{salt}"
                hashed_token = hashlib.sha512(full_token.encode()).hexdigest()
                token_exist = ApplicationToken.objects.filter(token=hashed_token).first()
                if not token_exist:
                    break
            ApplicationToken.objects.filter(application=obj).update(is_active=False)
            ApplicationToken.objects.create(
                application=obj,
                token=hashed_token,
                salt=salt,
            )
            messages.success(request, _(f"Token for {obj.name} created: {full_token}"))

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        PaymentSystemParamter.objects.filter(application_id=obj.id).exclude(payment_system=obj.payment_system).delete()
        existed_parameters = PaymentSystemParamter.objects.filter(
            application_id=obj.id, payment_system=obj.payment_system)
        existed_parameters_names = set([x.name for x in existed_parameters])
        parameters = set(PAYMENT_SYSTEM_PARAMETERS_MAP.get(obj.payment_system))
        if not parameters:
            return
        # Remove not existed parameteres in map
        params2delete = [name for name in existed_parameters_names if name not in parameters]
        if params2delete:
            PaymentSystemParamter.objects.filter(application_id=obj.id, name__in=params2delete).delete()
        for param in parameters:
            if param in existed_parameters_names:
                continue
            PaymentSystemParamter.objects.create(
                application_id=obj.id,
                payment_system=obj.payment_system,
                name=param,
            )


@admin.register(ApplicationToken)
class ApplicationTokenAdmin(ModelAdmin):
    list_display = ["application", "salt", "is_active"]
