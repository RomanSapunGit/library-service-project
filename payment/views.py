import stripe
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.viewsets import GenericViewSet

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
