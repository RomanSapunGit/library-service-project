from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Payment.Status)
    type = serializers.ChoiceField(choices=Payment.Type)

    class Meta:
        model = Payment
        fields = "__all__"


class PaymentDetailSerializer(PaymentSerializer):
    borrowing = serializers.SerializerMethodField()

    def get_borrowing(self, obj):
        from borrowing.serializers import BorrowingSerializer
        return BorrowingSerializer(obj.borrowing).data
