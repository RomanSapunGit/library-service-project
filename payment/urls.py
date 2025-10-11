from django.urls import path, include
from rest_framework import routers

from payment.views import PaymentView

router = routers.SimpleRouter()
router.register("", PaymentView, basename="payments")

urlpatterns = [path("", include(router.urls))]

app_name = "payment"
