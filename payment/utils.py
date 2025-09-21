import datetime

import stripe
from django.urls import reverse

from payment.models import Payment


def create_checkout_session(
        name,
        unit_amount,
        borrowing,
        request,
        payment_type
):
    session = stripe.checkout.Session.create(
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': name,
                },
                'unit_amount': unit_amount * 100,
            },
            'quantity': 1,
        }],
        mode="payment",
        success_url=request.build_absolute_uri(
            reverse("payment:payments-payment-success")
        ) + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=request.build_absolute_uri(
            reverse("payment:payments-payment-cancel")
        ) + "?session_id={CHECKOUT_SESSION_ID}",
    )

    return Payment.objects.create(
        status="PG",
        type=payment_type,
        borrowing=borrowing,
        session_url=session.url,
        session_id=session.id,
        money_to_pay=unit_amount
    )
