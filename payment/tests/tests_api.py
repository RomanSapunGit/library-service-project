from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from borrowing.models import Borrowing
from library.models import Book
from payment.models import Payment


# Create your tests here.
class PaymentTests(TestCase):
    def get_url(self, action):
        return reverse(f"payment:payments-{action}")

    def setUp(self):
        user = get_user_model()
        self.user = user.objects.create_user(
            email="user@user.com", password="pass123"
        )
        self.client = APIClient()

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

        self.payment = Payment.objects.create(
            status="PG",
            type="PT",
            session_url="https://stripe.com",
            session_id="123",
            money_to_pay=1234,
            borrowing=self.borrowing,
        )

    @patch("borrowing.task.send_telegram_message.delay")
    def test_payment_cancel(self, mock_send_message):
        mock_send_message.return_value.status_code = 200

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.get_url(action='payment-cancel')}?session_id=123")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    @patch("borrowing.task.send_telegram_message.delay")
    def test_payment_cancel_fail(self, mock_send_message):
        mock_send_message.return_value.status_code = 200

        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"{self.get_url(action='payment-cancel')}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("stripe.Webhook.construct_event")
    @patch("borrowing.task.send_telegram_message.delay")
    def test_payment_stripe_webhook(self, mock_send_message, mock_webhook_event):
        event = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "123"
                }
            }
        }
        mock_webhook_event.return_value = event
        mock_send_message.return_value.status_code = 200

        response = self.client.post(
            self.get_url(action="stripe-webhook"),
            HTTP_STRIPE_SIGNATURE="test"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, "PD")

    @patch("stripe.Webhook.construct_event")
    def test_payment_stripe_webhook_invalid_signature(self, mock_webhook_event):
        mock_webhook_event.side_effect = stripe.error.SignatureVerificationError(
            message="Invalid signature", http_body=None, sig_header=""
        )

        response = self.client.post(
            self.get_url(action="stripe-webhook"),
            HTTP_STRIPE_SIGNATURE="bad_signature"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch("stripe.Webhook.construct_event")
    def test_payment_stripe_webhook_invalid_payload(self, mock_webhook_event):
        mock_webhook_event.side_effect = ValueError("Invalid payload")

        payload = "not_json"

        response = self.client.post(
            self.get_url(action="stripe-webhook"),
            data=payload,
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="any_signature"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
