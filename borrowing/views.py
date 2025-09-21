from django.db import transaction

from rest_framework import viewsets
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin
)
from rest_framework.permissions import IsAuthenticated

from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingReturnSerializer
)


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
