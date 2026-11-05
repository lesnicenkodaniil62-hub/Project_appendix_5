from rest_framework import serializers

from .models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Lesson."""

    class Meta:
        model = Lesson
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Course с вложенными уроками."""

    # Количество уроков (задача 1)
    lessons_count = serializers.SerializerMethodField()

    # Вложенные уроки (задача 3)
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Course
        fields = "__all__"

    def get_lessons_count(self, course: Course) -> int:
        """Возвращает количество уроков в курсе."""
        return course.lessons.count()
