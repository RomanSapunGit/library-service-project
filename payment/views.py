import stripe
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from borrowing.task import send_telegram_message

from library_service import settings
from payment.models import Payment
from payment.serializers import PaymentSerializer, PaymentDetailSerializer



class PaymentView(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Payment.objects.all()
    filter_backends = (DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action == "detail":
            return PaymentDetailSerializer
        return PaymentSerializer

    stripe.api_key = settings.STRIPE_API_KEY

    @extend_schema(
        operation_id="payment_success",
        summary="Handle successful payment",
        description=(
                "Endpoint called after a successful Stripe Checkout session. "
                "It expects a `session_id` query parameter. "
                "Returns `204 No Content` if handled successfully."
        ),
        responses={
            204: OpenApiResponse(description="Payment success handled."),
            400: OpenApiResponse(description="No session_id provided."),
        },
        tags=["Payments"],
    )
    @action(detail=False)
    def payment_success(self, request):
        session_id = request.GET.get("session_id")

        if not session_id:
            return Response(
                {"error": "No session id provided!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        operation_id="payment_cancel",
        summary="Handle canceled payment",
        description=(
                "Endpoint called if a Stripe Checkout session is canceled. "
                "It expects a `session_id` query parameter. "
                "Triggers a Telegram notification and returns "
                "`204 No Content`."
        ),
        responses={
            204: OpenApiResponse(description="Payment cancel handled."),
            400: OpenApiResponse(description="No session_id provided."),
        },
        tags=["Payments"],
    )
    @action(detail=False)
    def payment_cancel(self, request):
        session_id = request.GET.get("session_id")

        if not session_id:
            return Response(
                {"error": "No session id provided!"},
                status=status.HTTP_400_BAD_REQUEST
            )

        send_telegram_message.delay(
            [
                "Payment was canceled.\n",
                "But do not need to worry, you can pay the borrowing anytime",
                "within the next 24 hours."
            ]
        )

        return Response(status=status.HTTP_204_NO_CONTENT)
