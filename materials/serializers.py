from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Lesson."""

    class Meta:
        model = Lesson
        fields = "__all__"
        # owner заполняется автоматически через perform_create()
        read_only_fields = ("owner",)


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course с вложенными уроками."""

    # Поле 1: количество уроков (из Задания 1)
    lessons_count = serializers.SerializerMethodField()

    # Поле 2: вложенные уроки (Задание 3)
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"
        # owner заполняется автоматически через perform_create()
        read_only_fields = ("owner",)

    def get_lessons_count(self, course: Course) -> int:
        """Возвращает количество уроков в курсе."""
        return course.lessons.count()