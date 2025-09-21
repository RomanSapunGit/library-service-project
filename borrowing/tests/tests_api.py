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

    def test_list_borrowings_as_staff(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.get_url())
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["id"], self.borrowing.id)

    @patch("stripe.checkout.Session.create")
    @patch("borrowing.task.send_telegram_message.delay")
    def test_create_borrowing_with_inventory(self, mock_send_message, mock_stripe):
        self.client.force_authenticate(user=self.user)
        payload = {
            "book": self.book.id,
            "expected_return_date": (timezone.now() + timezone.timedelta(days=7)).date(),
        }

        mock_send_message.return_value.status_code = 200
        mock_stripe.return_value.status_code = 200
        session = MockSession("123", "https://checkout.stripe.com/test")
        mock_stripe.return_value = session

        response = self.client.post(self.get_url(), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 1)

class MockSession:
    def __init__(self, id, url):
        self.id = id
        self.url = url
