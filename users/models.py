from __future__ import annotations

from typing import cast

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для модели пользователя с авторизацией по email."""

    def create_user(self, email: str, password: str | None = None, **extra_fields) -> User:
        """Создаёт и возвращает обычного пользователя с email и паролем."""
        if not email:
            raise ValueError("Пользователь должен иметь email-адрес")
        email = self.normalize_email(email)
        user = cast(User, self.model(email=email, **extra_fields))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields) -> User:
        """Создаёт и возвращает суперпользователя с email и паролем."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Кастомная модель пользователя с авторизацией по email."""

    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Введите email",
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Имя",
        help_text="Введите имя",
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name="Фамилия",
        help_text="Введите фамилию",
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
        verbose_name="Аватарка",
        help_text="Загрузите аватарку",
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Статус персонала",
        help_text="Имеет ли пользователь доступ к админ-панели",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен",
        help_text="Активен ли пользователь",
    )
    date_joined = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата регистрации",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return self.email


class Payment(models.Model):
    """Модель платежа за курс или урок."""

    PAYMENT_METHOD_CHOICES = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счет"),
    ]

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Пользователь",
        help_text="Пользователь, совершивший платеж",
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
        verbose_name="Оплаченный курс",
        help_text="Курс, который был оплачен",
    )
    lesson = models.ForeignKey(
        "materials.Lesson",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        verbose_name="Оплаченный урок",
        help_text="Урок, который был оплачен",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
        help_text="Сумма платежа",
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default="transfer",
        verbose_name="Способ оплаты",
        help_text="Выберите способ оплаты",
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-payment_date"]

    def __str__(self) -> str:
        paid_item = self.course.title if self.course else self.lesson.title if self.lesson else "Не указано"
        return f"Платеж {self.amount} руб. от {self.user.email} за {paid_item}"
