from django.db import models

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
