from django_filters.rest_framework import DjangoFilterBackend

from borrowing.filters import AdminBorrowingFilter, BorrowingFilter


class BorrowingFilterBackend(DjangoFilterBackend):
    def get_filterset_class(self, view, queryset=None):
        if view.request.user.is_staff:
            return AdminBorrowingFilter
        return BorrowingFilter
