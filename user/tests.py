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

    def test_create_superuser_with_is_staff_false_raises_error(self):
        with self.assertRaises(ValueError) as e:
            get_user_model().objects.create_superuser(
                email="admin@example.com",
                password="superpass123",
                is_staff=False
            )
        self.assertIn("is_staff=True", str(e.exception))

    def test_create_superuser_with_is_superuser_false_raises_error(self):
        with self.assertRaises(ValueError) as e:
            get_user_model().objects.create_superuser(
                email="admin@example.com",
                password="superpass123",
                is_superuser=False
            )
        self.assertIn("is_superuser=True", str(e.exception))

