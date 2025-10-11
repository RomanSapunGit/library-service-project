from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from library.models import Book
from library.serializers import BookDetailSerializer, BookSerializer
from utils.redis_utils import delete_book, create_book


# Create your views here.
class BookView(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        return BookSerializer

    def create(self, request, *args, **kwargs):
        create_book(request.data["inventory"])
        return super().create(request, *args, **kwargs)

    def perform_destroy(self, instance):
        delete_book(instance.inventory)