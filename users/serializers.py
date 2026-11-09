from rest_framework import serializers

from .models import Payment, User


class UserSerializer(serializers.ModelSerializer):
    """Базовый сериализатор для модели User."""

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


class UserRegisterSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
        )

    def validate_email(self, value):
        """Проверяет уникальность email."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate(self, attrs):
        """Проверяет совпадение паролей."""
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        """Создаёт пользователя с хешированным паролем."""
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfilePublicSerializer(serializers.ModelSerializer):
    """Публичный сериализатор для просмотра чужих профилей (без sensitive полей)."""

    class Meta:
        model = User
        # Общая информация: БЕЗ last_name и payments
        fields = (
            "id",
            "email",
            "first_name",
            "phone",
            "city",
            "avatar",
            "date_joined",
        )
        read_only_fields = fields


class PaymentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Payment с расширенной информацией."""

    course_title = serializers.CharField(source="course.title", read_only=True, default=None)
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


class UserProfilePrivateSerializer(serializers.ModelSerializer):
    """Приватный сериализатор для просмотра СВОЕГО профиля (с полной информацией)."""

    # Вложенные платежи — только для своего профиля
    payments = PaymentSerializer(many=True, read_only=True)

    class Meta:
        model = User
        # Полная информация: С last_name и payments
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",  # ← Есть только в приватном сериализаторе
            "phone",
            "city",
            "avatar",
            "date_joined",
            "payments",  # ← Есть только в приватном сериализаторе
        )
        read_only_fields = ("id", "date_joined")
