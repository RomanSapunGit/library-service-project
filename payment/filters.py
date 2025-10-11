import django_filters as filters

from payment.models import Payment


class PaymentFilter(filters.FilterSet):

    @property
    def qs(self):
        parent = super().qs
        user = getattr(self.request, "user", None)

        if user and not user.is_staff:
            parent = parent.filter(borrowing__user=user)
        return parent

    class Meta:
        model = Payment
        fields = ()
