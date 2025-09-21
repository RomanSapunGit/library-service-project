from rest_framework import serializers

from borrowing.models import Borrowing
from payment.serializers import PaymentSerializer


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
