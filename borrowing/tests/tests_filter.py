from datetime import timedelta, date

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from library.models import Book

class BorrowingFilterTests(TestCase):
    def setUp(self):
        user = get_user_model()
        self.user1 = user.objects.create_user(email="user1@test.com", password="pass123")
        self.user2 = user.objects.create_user(email="user2@test.com", password="pass123")
        self.staff = user.objects.create_user(email="staff@test.com", password="pass123", is_staff=True)

        self.book = Book.objects.create(title="Book1", author="Author", cover="HARD", inventory=2, daily_fee=1.5)

        today = date.today()
        self.borrowing_active = Borrowing.objects.create(
            user=self.user1,
            book=self.book,
            borrow_date=today,
            expected_return_date=today + timedelta(days=7),
            actual_return_date=None
        )

        self.borrowing_returned = Borrowing.objects.create(
            user=self.user1,
            book=self.book,
            borrow_date=today + timedelta(days=3),
            expected_return_date=today + timedelta(days=8),
            actual_return_date=today + timedelta(days=7)
        )

        self.borrowing_other = Borrowing.objects.create(
            user=self.user2,
            book=self.book,
            borrow_date=today,
            expected_return_date=today + timedelta(days=7),
            actual_return_date=None
        )
        self.client = APIClient()
        self.url = reverse("borrowing:borrowing-list")

    def test_non_staff_user_sees_only_their_borrowings(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.json()]
        self.assertIn(self.borrowing_active.id, ids)
        self.assertIn(self.borrowing_returned.id, ids)
        self.assertNotIn(self.borrowing_other.id, ids)

    def test_staff_can_filter_by_user_id(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(f"{self.url}?user_id={self.user1.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.json()
        ids = [item["id"] for item in data]

        self.assertIn(self.borrowing_active.id, ids)
        self.assertIn(self.borrowing_returned.id, ids)
        for item in data:
            self.assertEqual(item["user"], self.user1.id)

    def test_staff_can_filter_by_user_id_empty(self):
        self.client.force_authenticate(user=self.staff)

        response = self.client.get(f"{self.url}?user_id=")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        ids = [item["id"] for item in data]

        self.assertIn(self.borrowing_active.id, ids)
        self.assertIn(self.borrowing_returned.id, ids)
        self.assertIn(self.borrowing_other.id, ids)

    def test_filter_is_active_true(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(f"{self.url}?is_active=True")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        ids = [item["id"] for item in response.json()]
        self.assertIn(self.borrowing_active.id, ids)
        self.assertNotIn(self.borrowing_returned.id, ids)
