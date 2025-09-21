from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from library.models import Book


class BorrowingViewTests(TestCase):
    def setUp(self):
        user = get_user_model()
        self.user = user.objects.create_user(
            email="user@user.com", password="pass123"
        )
        self.staff = user.objects.create_user(
            email="admin@user.com", password="pass123", is_staff=True
        )
        self.book = Book.objects.create(
            title="Test Book",
            author="Author",
            cover="HARD",
            inventory=2,
            daily_fee=1.5,
        )
        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=timezone.now(),
            expected_return_date=timezone.now() + timezone.timedelta(days=7),
        )
        self.client = APIClient()

    def get_url(self, action=None, pk=None):
        if action and pk:
            return reverse(f"borrowing:borrowing-{action}", args=[pk])
        elif pk:
            return reverse("borrowing:borrowing-detail", args=[pk])
        return reverse("borrowing:borrowing-list")

    def test_list_borrowings_as_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], self.borrowing.id)
