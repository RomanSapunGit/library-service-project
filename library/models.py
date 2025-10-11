from django.db import models


# Create your models here.
class Book(models.Model):
    class Cover(models.TextChoices):
        HARD = "H", "Hard"
        SOFT = "S", "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=1,
        choices=Cover,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(decimal_places=2, max_digits=6)

    def __str__(self):
        return f"{self.author}: {self.title}"
