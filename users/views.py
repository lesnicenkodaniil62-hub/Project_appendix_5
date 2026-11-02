from rest_framework import generics

from .models import User
from .serializers import UserSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    """Generic-класс для редактирования профиля пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
