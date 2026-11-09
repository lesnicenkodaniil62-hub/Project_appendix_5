from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, viewsets

from users.permissions import IsNotModerator, IsOwner, IsOwnerOrModerator

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Course с разделением прав по action."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["owner", "title"]
    ordering_fields = ["id", "title"]
    ordering = ["-id"]

    def get_permissions(self):
        """Разделяет права доступа по action."""
        if self.action in ["list", "retrieve"]:
            # Все авторизованные могут просматривать
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            # Только обычные пользователи могут создавать (модераторы НЕ могут)
            self.permission_classes = [permissions.IsAuthenticated, IsNotModerator]
        elif self.action in ["update", "partial_update"]:
            # Владелец ИЛИ модератор могут редактировать
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        elif self.action == "destroy":
            # Только владелец может удалять (модераторы НЕ могут)
            self.permission_classes = [permissions.IsAuthenticated, IsNotModerator, IsOwner]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Автоматически заполняет owner при создании курса."""
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Generic-класс для получения списка уроков и создания нового урока."""

    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "title"]
    ordering_fields = ["id", "title"]
    ordering = ["id"]

    def get_permissions(self):
        """Разделяет права доступа по методу запроса."""
        if self.request.method == "GET":
            # Все авторизованные могут просматривать
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.request.method == "POST":
            # Только обычные пользователи могут создавать (модераторы НЕ могут)
            self.permission_classes = [permissions.IsAuthenticated, IsNotModerator]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Автоматически заполняет owner при создании урока."""
        serializer.save(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated]


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotModerator, IsOwner]
