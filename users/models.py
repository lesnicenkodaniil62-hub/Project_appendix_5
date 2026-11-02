from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    """Кастомный менеджер для модели пользователя с авторизацией по email."""

    def create_user(self, email, password=None, **extra_fields):
        """Создаёт и возвращает обычного пользователя с email и паролем."""
        if not email:
            raise ValueError("Пользователь должен иметь email-адрес")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
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
