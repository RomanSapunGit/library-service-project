from django.urls import include, path
from rest_framework import routers

from library.views import BookView

router = routers.SimpleRouter()
router.register("books", BookView)


urlpatterns = [path("", include(router.urls))]

app_name = "library"

