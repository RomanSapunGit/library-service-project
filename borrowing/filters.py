import django_filters as filters

from borrowing.models import Borrowing


class BorrowingFilter(filters.FilterSet):
    is_active = filters.BooleanFilter(
        field_name="actual_return_date",
        lookup_expr="isnull"
    )

    @property
    def qs(self):
        parent = super().qs
        user = getattr(self.request, "user", None)

        if user and not user.is_staff:
            parent = parent.filter(user=user)
        return parent

    class Meta:
        model = Borrowing
        fields = ["is_active"]
