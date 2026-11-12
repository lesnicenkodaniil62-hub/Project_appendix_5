from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Course, Lesson, Subscription
from .serializers import CourseSerializer, LessonSerializer
from users.permissions import IsModerator, IsNotModerator, IsOwner, IsOwnerOrModerator


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet для модели Course с разделением прав по action."""

    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["owner", "title"]
    ordering_fields = ["id", "title"]
    ordering = ["-id"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            self.permission_classes = [permissions.IsAuthenticated, IsNotModerator]
        elif self.action in ["update", "partial_update"]:
            self.permission_classes = [permissions.IsAuthenticated, IsOwnerOrModerator]
        elif self.action == "destroy":
            self.permission_classes = [permissions.IsAuthenticated, IsNotModerator, IsOwner]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
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
        if self.request.method == "GET":
            self.permission_classes = [permissions.IsAuthenticated]
        elif self.request.method == "POST":
            self.permission_classes = [permissions.IsAuthenticated, IsNotModerator]
        return [permission() for permission in self.permission_classes]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class LessonRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner | IsModerator]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonUpdateAPIView(generics.UpdateAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner | IsModerator]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class LessonDestroyAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [permissions.IsAuthenticated, IsNotModerator, IsOwner]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Модераторы").exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(owner=user)


class SubscriptionAPIView(APIView):
    """APIView для управления подпиской пользователя на курс (создание/удаление)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        course_id = request.data.get("course_id")

        if not course_id:
            return Response(
                {"error": "Необходимо указать course_id в теле запроса"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        course = get_object_or_404(Course, id=course_id)
        subs_item = Subscription.objects.filter(user=user, course=course)

        if subs_item.exists():
            # Если подписка есть — удаляем её
            subs_item.delete()
            message = "подписка удалена"
        else:
            # Если подписки нет — создаём её
            Subscription.objects.create(user=user, course=course)
            message = "подписка добавлена"

        return Response({"message": message}, status=status.HTTP_200_OK)
