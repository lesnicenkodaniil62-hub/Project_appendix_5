from rest_framework import serializers

from .models import Payment, User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User (редактирование профиля)."""

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "date_joined",
        )
        read_only_fields = ("id", "date_joined")


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Payment с расширенной информацией."""

    # Расширяем: показываем название курса вместо ID
    course_title = serializers.CharField(source="course.title", read_only=True, default=None)
    # Расширяем: показываем название урока вместо ID
    lesson_title = serializers.CharField(source="lesson.title", read_only=True, default=None)

    class Meta:
        model = Payment
        fields = (
            "id",
            "user",
            "payment_date",
            "course",
            "course_title",
            "lesson",
            "lesson_title",
            "amount",
            "payment_method",
        )


class UserWithPaymentsSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя с историей платежей."""

    # Вложенные платежи с расширенной информацией
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
            "date_joined",
            "payments",
        )
        read_only_fields = ("id", "date_joined")
