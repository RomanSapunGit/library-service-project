from datetime import timedelta, date

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from library.models import Book
from payment.models import Payment


class PaymentFilterTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user1 = user_model.objects.create_user(email="user1@test.com", password="pass123")
        self.user2 = user_model.objects.create_user(email="user2@test.com", password="pass123")
        self.staff = user_model.objects.create_user(email="staff@test.com", password="pass123", is_staff=True)

        self.book = Book.objects.create(title="Book1", author="Author", cover="HARD", inventory=2, daily_fee=1.5)
        today = date.today()

        self.borrowing1 = Borrowing.objects.create(user=self.user1, book=self.book, borrow_date=today,
                                                   expected_return_date=today + timedelta(days=7))
        self.borrowing2 = Borrowing.objects.create(user=self.user2, book=self.book, borrow_date=today,
                                                   expected_return_date=today + timedelta(days=7))

        self.payment1 = Payment.objects.create(
            status="PG", type="PT", session_url="https://stripe.com/1", session_id="p1",
            money_to_pay=100, borrowing=self.borrowing1
        )
        self.payment2 = Payment.objects.create(
            status="PD", type="PT", session_url="https://stripe.com/2", session_id="p2",
            money_to_pay=150, borrowing=self.borrowing1
        )
        self.payment3 = Payment.objects.create(
            status="PG", type="PT", session_url="https://stripe.com/3", session_id="p3",
            money_to_pay=200, borrowing=self.borrowing2
        )

        self.client = APIClient()
        self.url = reverse("payment:payments-list")

    def test_non_staff_user_sees_only_their_payments(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.json()]

        self.assertIn(self.payment1.id, returned_ids)
        self.assertIn(self.payment2.id, returned_ids)

        self.assertNotIn(self.payment3.id, returned_ids)

    def test_non_staff_user_sees_all_payments(self):
        self.client.force_authenticate(user=self.staff)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        returned_ids = [item["id"] for item in response.json()]

        self.assertIn(self.payment1.id, returned_ids)
        self.assertIn(self.payment2.id, returned_ids)
        self.assertIn(self.payment3.id, returned_ids)
