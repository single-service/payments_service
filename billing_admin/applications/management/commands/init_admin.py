import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Init Admin user'


    def handle(self, *args, **options):
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin")

        # check if user exist
        is_user_exist = User.objects.filter(username=admin_username).exists()
        if is_user_exist:
            return
        admin_user = User.objects.create_user(
            email=admin_username,
            username=admin_username
        )
        admin_user.set_password(admin_password)
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.is_active = True
        admin_user.save()