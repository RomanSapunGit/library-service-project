from datetime import timedelta, date

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
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
