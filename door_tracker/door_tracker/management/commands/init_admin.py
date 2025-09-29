import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Upsert a superuser, with credentials taken from process environment.'
    requires_migrations_checks = True
    output_transaction = True

    def handle(self, *args, **options):
        username = os.getenv('ADMIN_USER', 'admin')
        email = os.getenv('ADMIN_EMAIL', None)
        password = os.getenv('ADMIN_PASS', None)
        try:
            u = User.objects.get(username=username)
            u.email = email or ''
            u.set_password(password)
            u.save()
        except User.DoesNotExist:
            User.objects.create_superuser(username, email=email, password=password)
