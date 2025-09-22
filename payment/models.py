from django.db import models

from borrowing.models import Borrowing


# Create your models here.
class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PG", "Pending"
        PAID = "PD", "Paid"

    class Type(models.TextChoices):
        PAYMENT = "PT", "Payment"
        FINE = "F", "Fine"

    status = models.CharField(
        max_length=2,
        choices=Status
    )
    type = models.CharField(
        max_length=2,
        choices=Type
    )
    borrowing = models.ForeignKey(
        Borrowing,
        on_delete=models.CASCADE,
        related_name="payments"
    )
    session_url = models.URLField(max_length=500)
    session_id = models.TextField()
    money_to_pay = models.DecimalField(decimal_places=2, max_digits=7)
