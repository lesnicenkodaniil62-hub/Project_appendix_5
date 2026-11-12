from rest_framework import serializers

from .models import Course, Lesson, Subscription
from .validators import validate_youtube_url


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Lesson."""

    video_url = serializers.URLField(
        validators=[validate_youtube_url],
        required=False,
        allow_null=True,
        help_text="Ссылка должна вести на youtube.com"
    )

    class Meta:
        model = Lesson
        fields = "__all__"
        read_only_fields = ("owner",)


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course с вложенными уроками и признаком подписки."""

    lessons_count = serializers.SerializerMethodField()
    lessons = LessonSerializer(many=True, read_only=True)

    # ⭐ Новое поле: признак подписки текущего пользователя
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("owner",)

    def get_lessons_count(self, course: Course) -> int:
        """Возвращает количество уроков в курсе."""
        return course.lessons.count()

    def get_is_subscribed(self, course: Course) -> bool:
        """Проверяет, подписан ли текущий пользователь на этот курс."""
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, course=course).exists()
        return False
