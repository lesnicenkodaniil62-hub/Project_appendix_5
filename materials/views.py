from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, viewsets

from users.permissions import IsModerator, IsNotModerator, IsOwner

from .models import Course, Lesson
from .serializers import CourseSerializer, LessonSerializer


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Course с разделением прав по action."""

    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["owner", "title"]
    ordering_fields = ["id", "title"]
    ordering = ["-id"]

    def get_queryset(self):
        """Возвращает queryset с фильтрацией по владельцу."""
        user = self.request.user
        # Модераторы видят все курсы
        if user.groups.filter(name="Модераторы").exists():
            return Course.objects.all()
        # Обычные пользователи видят только свои курсы
        return Course.objects.filter(owner=user)

    def get_permissions(self):
        """Разделяет права доступа по action."""
        if self.action in ["list", "retrieve"]:
            # Все авторизованные могут просматривать (но только свои, кроме модераторов)
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            # Только обычные пользователи могут создавать (модераторы НЕ могут)
            self.permission_classes = [permissions.IsAuthenticated, IsNotModerator]
        elif self.action in ["update", "partial_update"]:
            # Владелец ИЛИ модератор могут редактировать
            self.permission_classes = [permissions.IsAuthenticated, IsOwner | IsModerator]
        elif self.action == "destroy":
            # Только владелец может удалять (модераторы НЕ могут)
            self.permission_classes = [permissions.IsAuthenticated, IsNotModerator, IsOwner]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        """Автоматически заполняет owner при создании курса."""
        serializer.save(owner=self.request.user)


class LessonListCreateAPIView(generics.ListCreateAPIView):
    """Generic-класс для получения списка уроков и создания нового урока."""

    serializer_class = LessonSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["course", "title"]
    ordering_fields = ["id", "title"]
    ordering = ["id"]

    def get_queryset(self):
        """Возвращает queryset с фильтрацией по владельцу."""
        user = self.request.user
        # Модераторы видят все уроки
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        # Обычные пользователи видят только свои уроки
        return Lesson.objects.filter(owner=user)

    def get_permissions(self):
        """Разделяет права доступа по методу запроса."""
        if self.request.method == "GET":
            # Все авторизованные могут просматривать (но только свои, кроме модераторов)
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
    permission_classes = [permissions.IsAuthenticated, IsOwner | IsModerator]

    def get_queryset(self):
        """Возвращает queryset с фильтрацией по владельцу."""
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner | IsModerator]

    def get_queryset(self):
        """Возвращает queryset с фильтрацией по владельцу."""
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotModerator, IsOwner]

    def get_queryset(self):
        """Возвращает queryset с фильтрацией по владельцу."""
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)
