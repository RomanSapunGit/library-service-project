from django.db import transaction
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.backends import BorrowingFilterBackend

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer
)
from borrowing.task import send_telegram_message
from library.models import Book
from payment.serializers import PaymentSerializer
from payment.utils import create_checkout_borrowing_session


# Create your views here.
class BorrowingView(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.select_related("book")
    filter_backends = (BorrowingFilterBackend,)
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "return_book":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    @extend_schema(
        operation_id="borrow_book",
        summary="Borrow a book",
        description=(
                "Creates a borrowing record for the given book. "
                "If the book is available (inventory > 0), its "
                "inventory is decreased, "
                "a payment checkout session is created, and a "
                "Telegram notification is sent. "
                "If no copies are available, returns an error."
        ),
        request=BorrowingSerializer,
        responses={
            201: OpenApiResponse(
                response=BorrowingSerializer,
                description="Borrowing created successfully. "
                            "Response includes payment session details."
            ),
            400: OpenApiResponse(
                description="The book inventory is empty."
            ),
        },
        tags=["Borrowings"],
    )
    def create(self, request, *args, **kwargs):
        book = Book.objects.get(pk=request.data["book"])
        if book.inventory >= 1:
            with transaction.atomic():
                book.inventory -= 1
                book.save()
                result = super().create(request, *args, **kwargs)
                send_telegram_message.delay(
                    [
                        f"Book with id {book.id} is borrowed.",
                        f"Expected return date is: "
                        f"{result.data['expected_return_date']}"
                    ]
                )
                borrowing = self.get_queryset().get(pk=result.data["id"])
                payment = create_checkout_borrowing_session(borrowing, request)
                payment_serializer = PaymentSerializer(payment)
                payments = list(result.data["payments"])
                payments.append(payment_serializer.data)
                result.data["payments"] = payments
                return result
        return Response(
            data={"error": "books inventory is empty!"},
            status=status.HTTP_400_BAD_REQUEST
        )

    @extend_schema(
        operation_id="return_book",
        summary="Return a borrowed book",
        description=(
                "Marks a borrowing as returned. "
                "If returned late, a payment session is created for the fine. "
                "If returned on time, the book inventory is increased by 1."
        ),
        request=None,
        responses={
            200: OpenApiResponse(
                response=BorrowingSerializer,
                description="Book returned successfully. Response "
                            "includes borrowing details "
                            "(and payment if late)."
            ),
            400: OpenApiResponse(
                description="The book has already been returned."
            ),
        },
        tags=["Borrowings"],
    )
    @action(detail=True, methods=["post"])
    def return_book(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            borrowing.actual_return_date = timezone.localdate()
            if borrowing.actual_return_date > borrowing.expected_return_date:
                payment = create_checkout_borrowing_session(
                    borrowing,
                    request,
                    2,
                    "F"
                )
                borrowing.payments.add(payment)
                borrowing_serializer = BorrowingSerializer(borrowing)
                return Response(
                    borrowing_serializer.data,
                    status=status.HTTP_200_OK
                )

            borrowing.save()

            book = borrowing.book
            book.inventory += 1
            book.save()

        serializer = self.get_serializer(borrowing)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
