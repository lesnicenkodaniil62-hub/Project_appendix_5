from rest_framework import generics, viewsets

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Course (CRUD через ViewSet)."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Generic-класс для получения списка уроков и создания нового урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    """Generic-класс для получения одного урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonUpdateAPIView(generics.UpdateAPIView):
    """Generic-класс для обновления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer


class LessonDestroyAPIView(generics.DestroyAPIView):
    """Generic-класс для удаления урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
