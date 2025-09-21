from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


# Create your tests here.
class ModelTests(TestCase):
    def test_create_superuser_success(self):
        superuser = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="superpass123"
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertEqual(superuser.email, "admin@example.com")
        self.assertTrue(superuser.check_password("superpass123"))

