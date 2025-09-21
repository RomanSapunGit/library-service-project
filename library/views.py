from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from library.models import Book
from library.serializers import BookDetailSerializer, BookSerializer


# Create your views here.
class BookView(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return BookDetailSerializer
        return BookSerializer
