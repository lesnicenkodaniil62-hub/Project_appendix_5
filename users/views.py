import stripe
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.response import Response

from materials.models import Course

from .models import Payment, User
from .permissions import IsOwner
from .serializers import (
    PaymentSerializer,
    UserProfilePrivateSerializer,
    UserProfilePublicSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
from .services import (
    create_stripe_price,
    create_stripe_product,
    create_stripe_session,
    get_stripe_session_status,
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
    """Эндпоинт для просмотра профиля пользователя."""

    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        profile_user = self.get_object()
        if profile_user == self.request.user:
            return UserProfilePrivateSerializer
        return UserProfilePublicSerializer


class UserUpdateAPIView(generics.UpdateAPIView):
    """Эндпоинт для редактирования профиля пользователя."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
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


class PaymentCreateAPIView(generics.CreateAPIView):
    """
    Создание платежа через Stripe.
    Принимает course_id и amount, создает продукт, цену и сессию в Stripe,
    сохраняет данные в локальную модель Payment и возвращает ссылку на оплату.
    """

    serializer_class = PaymentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        course_id = request.data.get("course")
        amount = request.data.get("amount")

        if not course_id or not amount:
            return Response(
                {"error": "Необходимо указать 'course' и 'amount'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(Course, id=course_id)

        try:
            # 1. Создаем продукт в Stripe
            product_id = create_stripe_product(
                name=f"Курс: {course.title}",
                description=course.description or "Оплата курса",
            )

            # 2. Создаем цену в Stripe (функция сама умножит на 100)
            price_id = create_stripe_price(
                product_id=product_id,
                amount=float(amount),
            )

            # 3. Создаем сессию оплаты
            success_url = request.build_absolute_uri("/payments/success/")
            cancel_url = request.build_absolute_uri("/payments/cancel/")

            session_data = create_stripe_session(
                price_id=price_id,
                success_url=success_url,
                cancel_url=cancel_url,
            )

            # 4. Сохраняем платеж в нашей базе данных
            payment = Payment.objects.create(
                user=request.user,
                course=course,
                amount=amount,
                payment_method="card",
                stripe_product_id=product_id,
                stripe_price_id=price_id,
                stripe_session_id=session_data["id"],
                payment_url=session_data["url"],
                status="pending",
            )

            serializer = self.get_serializer(payment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except stripe.error.StripeError as e:
            return Response(
                {"error": f"Ошибка платежной системы: {str(e)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )


class PaymentStatusAPIView(generics.RetrieveAPIView):
    """
    Проверка статуса платежа по session_id.
    Синхронизирует статус с локальной моделью Payment.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        session_id = kwargs.get("session_id")

        # ⭐ Явная проверка на None (исправление mypy ошибки)
        if not session_id:
            return Response(
                {"error": "Не указан session_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Находим платеж, принадлежащий текущему пользователю
        payment = get_object_or_404(
            Payment,
            stripe_session_id=session_id,
            user=request.user,
        )

        try:
            # Запрашиваем актуальный статус из Stripe
            stripe_status = get_stripe_session_status(session_id)

            # Синхронизируем с нашей моделью
            if stripe_status == "paid":
                payment.status = "paid"
                payment.save(update_fields=["status"])
            elif stripe_status == "unpaid":
                payment.status = "canceled"
                payment.save(update_fields=["status"])

            return Response(
                {
                    "session_id": session_id,
                    "stripe_status": stripe_status,
                    "local_status": payment.status,
                    "payment_url": payment.payment_url,
                }
            )
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
