from rest_framework import serializers

from borrowing.models import Borrowing
from library.serializers import BookDetailSerializer
from payment.serializers import PaymentSerializer
from user.serializers import UserSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(read_only=True, many=True)

    class Meta:
        model = Borrowing
        fields = ("id", "book", "expected_return_date", "user", "payments")
        read_only_fields = ["id", "user"]

class BorrowingReturnSerializer(BorrowingSerializer):

    class Meta:
        model = Borrowing
        fields = BorrowingSerializer.Meta.fields + ("actual_return_date",)

class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookDetailSerializer()
    user = UserSerializer()
