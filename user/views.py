from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from user.serializers import UserSerializer


# Create your views here.
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

