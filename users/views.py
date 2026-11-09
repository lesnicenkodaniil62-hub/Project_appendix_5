from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, viewsets

from .models import Payment, User
from .serializers import (
    PaymentSerializer,
    UserRegisterSerializer,
    UserSerializer,
    UserWithPaymentsSerializer,
)


class UserRegisterAPIView(generics.CreateAPIView):
    """Публичный эндпоинт для регистрации нового пользователя."""

    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [permissions.AllowAny]  # ← Открыт для всех


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet для CRUD операций с пользователями (защищён авторизацией)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # ← Только для авторизованных


class UserProfileAPIView(generics.RetrieveAPIView):
    """Generic-класс для получения профиля пользователя с историей платежей."""

    queryset = User.objects.all()
    serializer_class = UserWithPaymentsSerializer
    permission_classes = [permissions.IsAuthenticated]  # ← Только для авторизованных


class UserUpdateAPIView(generics.UpdateAPIView):
    """Generic-класс для редактирования профиля пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]  # ← Только для авторизованных


class PaymentListAPIView(generics.ListAPIView):
    """Generic-класс для получения списка платежей с фильтрацией и сортировкой."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]  # ← Только для авторизованных
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "lesson", "payment_method"]
    ordering_fields = ["payment_date"]
    ordering = ["-payment_date"]
