from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для модели User, где email является уникальным идентификатором."""

    def create_user(self, email, password=None, **extra_fields):  # type: ignore[no-untyped-def]
        """Создаёт и возвращает обычного пользователя."""
        if not email:
            raise ValueError("Поле Email должно быть заполнено")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # type: ignore[attr-defined]
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):  # type: ignore[no-untyped-def]
        """Создаёт и возвращает суперпользователя."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Кастомная модель пользователя."""

    username = None  # type: ignore[assignment]
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Введите email",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Телефон",
        help_text="Введите номер телефона",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Город",
        help_text="Введите город",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name="Аватар",
        help_text="Загрузите аватар",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    # Переопределяем менеджер с подавлением ВСЕХ ошибок mypy на этой строке
    objects = CustomUserManager()  # type: ignore

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.email


class Payment(models.Model):
    """Модель платежа."""

    PAYMENT_METHODS = [
        ("cash", "Наличные"),
        ("transfer", "Перевод"),
        ("card", "Банковская карта (Stripe)"),
    ]

    PAYMENT_STATUSES = [
        ("pending", "Ожидает оплаты"),
        ("paid", "Оплачен"),
        ("canceled", "Отменен"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
    )
    payment_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата оплаты",
    )
    course = models.ForeignKey(
        "materials.Course",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Курс",
    )
    lesson = models.ForeignKey(
        "materials.Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Урок",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        verbose_name="Способ оплаты",
    )
    stripe_product_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID продукта в Stripe",
    )
    stripe_price_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID цены в Stripe",
    )
    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="ID сессии в Stripe",
    )
    payment_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на оплату",
    )
    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUSES,
        default="pending",
        verbose_name="Статус платежа",
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]

    def __str__(self) -> str:
        return f"Платеж {self.amount} от {self.user.email}"
