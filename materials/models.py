from django.conf import settings
from django.db import models


class Course(models.Model):
    """Модель курса."""

    title = models.CharField(
        max_length=200,
        verbose_name="Название",
        help_text="Введите название курса",
    )
    preview = models.ImageField(
        upload_to="materials/courses/previews/",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите превью курса",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Введите описание курса",
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="courses",
        verbose_name="Владелец",
        help_text="Пользователь, создавший курс",
    )

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"
        ordering = ["-id"]

    def __str__(self) -> str:
        return self.title


class Lesson(models.Model):
    """Модель урока."""

    title = models.CharField(
        max_length=200,
        verbose_name="Название",
        help_text="Введите название урока",
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name="Описание",
        help_text="Введите описание урока",
    )
    preview = models.ImageField(
        upload_to="materials/lessons/previews/",
        blank=True,
        null=True,
        verbose_name="Превью",
        help_text="Загрузите превью урока",
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        verbose_name="Ссылка на видео",
        help_text="Введите ссылку на видео",
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
        help_text="Курс, к которому относится урок",
    )
    # НОВОЕ ПОЛЕ: владелец урока
    owner = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Владелец",
        help_text="Пользователь, создавший урок",
        null=True,  # Временно разрешаем null для существующих записей
        blank=True,
    )

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["course", "id"]

    def __str__(self) -> str:
        return f"{self.title} (Курс: {self.course.title})"


class Subscription(models.Model):
    """Модель подписки пользователя на курс."""

    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Пользователь",
    )
    course = models.ForeignKey(
        "Course",
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата подписки",
    )

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        # Гарантируем уникальность пары пользователь + курс
        constraints = [
            models.UniqueConstraint(
                fields=["user", "course"],
                name="unique_user_course_subscription",
            )
        ]

    def __str__(self) -> str:
        return f"Подписка {self.user.email} на курс '{self.course.title}'"
