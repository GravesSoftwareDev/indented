import os
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Creates a superuser from environment variables if one does not already exist'

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.getenv('DJANGO_SUPERUSER_USERNAME')
        email = os.getenv('DJANGO_SUPERUSER_EMAIL', '')
        password = os.getenv('DJANGO_SUPERUSER_PASSWORD')

        if not username or not password:
            self.stdout.write('Skipping superuser creation: DJANGO_SUPERUSER_USERNAME and DJANGO_SUPERUSER_PASSWORD are not set.')
            return

        user, created = User.objects.get_or_create(username=username, defaults={'email': email})
        if created:
            user.is_staff = True
            user.is_superuser = True
        user.set_password(password)
        user.save()
        action = 'created' if created else 'updated'
        self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" {action}.'))
