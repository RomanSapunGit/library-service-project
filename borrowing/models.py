from django.db import models
from django.db.models import Q, F

from library.models import Book
from user.models import User


# Create your models here.
class Borrowing(models.Model):
    borrow_date = models.DateField(
        auto_now_add=True,
    )
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True)
    book = models.ForeignKey("library.book", on_delete=models.CASCADE)
    user = models.ForeignKey("user.user", on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(expected_return_date__gt=F("borrow_date")),
                name="expected_after_borrow",
            ),
            models.CheckConstraint(
                check=(
                    Q(actual_return_date__isnull=True)
                    | Q(actual_return_date__gte=F("borrow_date"))
                ),
                name="actual_after_borrow",
            ),
        ]
