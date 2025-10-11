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

class AdminBorrowingFilter(BorrowingFilter):
    user_id = filters.NumberFilter(method="filter_user_id")

    def filter_user_id(self, queryset, name, value):
        if not value:
            return queryset
        return queryset.filter(user=value)

    class Meta:
        fields = ["user_id", "is_active"]
