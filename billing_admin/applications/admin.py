import string
import hashlib
import secrets
import random

from django.contrib import admin, messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.utils.html import format_html
from django.utils.translation import gettext as _

from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import Application, ApplicationToken


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    pass


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass



@admin.register(Application)
class ApplicationAdmin(ModelAdmin):
    actions = ['create_token']

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


@admin.register(ApplicationToken)
class ApplicationTokenAdmin(ModelAdmin):
    list_display = ["application", "salt", "is_active"]