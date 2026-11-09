from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, viewsets

from .models import Payment, User
from .permissions import IsOwner
from .serializers import (
    PaymentSerializer,
    UserProfilePrivateSerializer,
    UserProfilePublicSerializer,
    UserRegisterSerializer,
    UserSerializer,
)


class UserRegisterAPIView(generics.CreateAPIView):
    """Публичный эндпоинт для регистрации нового пользователя."""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserProfileAPIView(generics.RetrieveAPIView):
    """
    Эндпоинт для просмотра профиля пользователя.
    - Свой профиль: полная информация (с last_name и payments)
    - Чужой профиль: только общая информация (без last_name и payments)
    """

    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от того, свой ли это профиль."""
        # Получаем объект профиля
        profile_user = self.get_object()
        # Если это свой профиль — используем приватный сериализатор
        if profile_user == self.request.user:
            return UserProfilePrivateSerializer
        # Если чужой — используем публичный
        return UserProfilePublicSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    """
    Эндпоинт для редактирования профиля пользователя.
    Редактировать можно ТОЛЬКО свой профиль.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    # IsOwner — можно редактировать только свой профиль
    permission_classes = [permissions.IsAuthenticated, IsOwner]


class PaymentListAPIView(generics.ListAPIView):
    """Generic-класс для получения списка платежей с фильтрацией и сортировкой."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]
