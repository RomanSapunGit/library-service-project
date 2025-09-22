import time

from django.contrib.auth import get_user_model
from django.db import connections
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = "Create a test user"

    def handle(self, *args, **kwargs):
        user = get_user_model()
        if not user.objects.filter(email="user@user.com").exists():
            user.objects.create_user(email="user@user.com", password="pass123")
            self.stdout.write(self.style.SUCCESS("Test user created!"))
        else:
            self.stdout.write(self.style.WARNING("User already exists"))
