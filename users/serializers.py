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
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email уже существует")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError({"password_confirm": "Пароли не совпадают"})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserProfilePublicSerializer(serializers.ModelSerializer):
    """Публичный сериализатор для просмотра чужих профилей."""

    class Meta:
        model = User
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
    """Сериализатор для модели Payment с полями Stripe."""

    course_title = serializers.CharField(
        source="course.title",
        read_only=True,
        default=None,
    )
    lesson_title = serializers.CharField(
        source="lesson.title",
        read_only=True,
        default=None,
    )

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
            "stripe_product_id",
            "stripe_price_id",
            "stripe_session_id",
            "payment_url",
            "status",
        )
        read_only_fields = (
            "id",
            "payment_date",
            "user",
            "stripe_product_id",
            "stripe_price_id",
            "stripe_session_id",
            "payment_url",
            "status",
        )


class UserProfilePrivateSerializer(serializers.ModelSerializer):
    """Приватный сериализатор для просмотра СВОЕГО профиля."""

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
