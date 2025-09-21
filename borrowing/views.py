from django.db import transaction

from rest_framework import viewsets, status
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer
)
from library.models import Book


# Create your views here.
class BorrowingView(
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = Borrowing.objects.select_related("book")
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "return_book":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def create(self, request, *args, **kwargs):
        book = Book.objects.get(pk=request.data["book"])
        if book.inventory >= 1:
            with transaction.atomic():
                book.inventory -= 1
                book.save()
                result = super().create(request, *args, **kwargs)
                return result
        return Response(
            data={"error": "books inventory is empty!"},
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
