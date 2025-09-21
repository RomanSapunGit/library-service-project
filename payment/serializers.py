from rest_framework import serializers

from payment.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Payment.Status)
    type = serializers.ChoiceField(choices=Payment.Type)

    class Meta:
        model = Payment
        fields = "__all__"
