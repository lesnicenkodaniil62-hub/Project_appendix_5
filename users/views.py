from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics

from .models import Payment, User
from .serializers import PaymentSerializer, UserSerializer, UserWithPaymentsSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    """Generic-класс для редактирования профиля пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserProfileAPIView(generics.RetrieveAPIView):
    """Generic-класс для получения профиля пользователя с историей платежей."""

    queryset = User.objects.all()
    serializer_class = UserWithPaymentsSerializer


class PaymentListAPIView(generics.ListAPIView):
    """Generic-класс для получения списка платежей с фильтрацией и сортировкой."""

    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    # Подключаем фильтры и сортировку
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    # Фильтры: по курсу, уроку и способу оплаты
    filterset_fields = ["course", "lesson", "payment_method"]
    # Сортировка: по дате оплаты
    ordering_fields = ["payment_date"]
    # Сортировка по умолчанию (новые платежи сверху)
    ordering = ["-payment_date"]
