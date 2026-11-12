from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import User

from .models import Course, Lesson, Subscription


class LessonCRUDTests(APITestCase):
    """Тесты CRUD операций для уроков."""

    def setUp(self):
        """Создаёт тестовые данные."""
        # Создаём группу модераторов
        self.moderator_group = Group.objects.create(name="Модераторы")

        # Создаём обычного пользователя
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
            first_name="Обычный",
            last_name="Пользователь",
        )

        # Создаём модератора
        self.moderator = User.objects.create_user(
            email="moderator@test.com",
            password="testpass123",
            first_name="Модератор",
            last_name="Тестовый",
        )
        self.moderator.groups.add(self.moderator_group)

        # Создаём второго обычного пользователя
        self.user2 = User.objects.create_user(
            email="user2@test.com",
            password="testpass123",
            first_name="Второй",
            last_name="Пользователь",
        )

        # Создаём курс
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание курса",
            owner=self.user,
        )

        # Создаём урок
        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Описание урока",
            video_url="https://www.youtube.com/watch?v=test",
            course=self.course,
            owner=self.user,
        )

    def test_create_lesson_by_user(self):
        """Обычный пользователь может создать урок."""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Новый урок",
            "description": "Описание",
            "video_url": "https://www.youtube.com/watch?v=new",
            "course": self.course.id,
        }
        response = self.client.post("/materials/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_create_lesson_by_moderator_forbidden(self):
        """Модератор НЕ может создать урок."""
        self.client.force_authenticate(user=self.moderator)
        data = {
            "title": "Урок модератора",
            "description": "Описание",
            "video_url": "https://www.youtube.com/watch?v=mod",
            "course": self.course.id,
        }
        response = self.client.post("/materials/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_lessons_list(self):
        """Авторизованный пользователь может получить список уроков."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/materials/lessons/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Пользователь видит только свои уроки
        self.assertEqual(len(response.data["results"]), 1)

    def test_get_lesson_detail_by_owner(self):
        """Владелец может получить детали своего урока."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/materials/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Тестовый урок")

    def test_get_lesson_detail_by_moderator(self):
        """Модератор может получить детали любого урока."""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.get(f"/materials/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_lesson_by_owner(self):
        """Владелец может обновить свой урок."""
        self.client.force_authenticate(user=self.user)
        data = {"title": "Обновлённый урок"}
        response = self.client.patch(f"/materials/lessons/{self.lesson.id}/update/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lesson.refresh_from_db()
        self.assertEqual(self.lesson.title, "Обновлённый урок")

    def test_update_lesson_by_moderator(self):
        """Модератор может обновить любой урок."""
        self.client.force_authenticate(user=self.moderator)
        data = {"title": "Обновлено модератором"}
        response = self.client.patch(f"/materials/lessons/{self.lesson.id}/update/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_lesson_by_other_user_forbidden(self):
        """Другой пользователь НЕ может обновить чужой урок."""
        self.client.force_authenticate(user=self.user2)
        data = {"title": "Попытка взлома"}
        response = self.client.patch(f"/materials/lessons/{self.lesson.id}/update/", data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_lesson_by_owner(self):
        """Владелец может удалить свой урок."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/materials/lessons/{self.lesson.id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_delete_lesson_by_moderator_forbidden(self):
        """Модератор НЕ может удалить урок."""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(f"/materials/lessons/{self.lesson.id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_lesson_by_other_user_forbidden(self):
        """Другой пользователь НЕ может удалить чужой урок."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f"/materials/lessons/{self.lesson.id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_lesson_without_auth(self):
        """Неавторизованный пользователь НЕ может создать урок."""
        data = {
            "title": "Урок без авторизации",
            "description": "Описание",
            "video_url": "https://www.youtube.com/watch?v=noauth",
            "course": self.course.id,
        }
        response = self.client.post("/materials/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class YouTubeValidatorTests(APITestCase):
    """Тесты валидации YouTube URL."""

    def setUp(self):
        """Создаёт тестовые данные."""
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание",
            owner=self.user,
        )

    def test_valid_youtube_url(self):
        """Валидная ссылка на YouTube проходит валидацию."""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Урок с YouTube",
            "description": "Описание",
            "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "course": self.course.id,
        }
        response = self.client.post("/materials/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_invalid_youtube_url(self):
        """Ссылка на сторонний ресурс не проходит валидацию."""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Урок с Stepik",
            "description": "Описание",
            "video_url": "https://stepik.org/lesson/123",
            "course": self.course.id,
        }
        response = self.client.post("/materials/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("video_url", response.data)


class SubscriptionTests(APITestCase):
    """Тесты функционала подписки на курс."""

    def setUp(self):
        """Создаёт тестовые данные."""
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание",
            owner=self.user,
        )

    def test_subscribe_to_course(self):
        """Пользователь может подписаться на курс."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/materials/courses/subscribe/",
            {"course_id": self.course.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка добавлена")
        self.assertTrue(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_unsubscribe_from_course(self):
        """Пользователь может отписаться от курса."""
        # Сначала подписываемся
        Subscription.objects.create(user=self.user, course=self.course)

        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/materials/courses/subscribe/",
            {"course_id": self.course.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")
        self.assertFalse(Subscription.objects.filter(user=self.user, course=self.course).exists())

    def test_subscribe_without_course_id(self):
        """Подписка без course_id возвращает ошибку."""
        self.client.force_authenticate(user=self.user)
        response = self.client.post("/materials/courses/subscribe/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscribe_without_auth(self):
        """Неавторизованный пользователь не может подписаться."""
        response = self.client.post(
            "/materials/courses/subscribe/",
            {"course_id": self.course.id},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_is_subscribed_field_in_course_serializer(self):
        """Поле is_subscribed присутствует в сериализаторе курса."""
        self.client.force_authenticate(user=self.user)
        Subscription.objects.create(user=self.user, course=self.course)

        response = self.client.get(f"/materials/courses/{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("is_subscribed", response.data)
        self.assertTrue(response.data["is_subscribed"])

    def test_is_not_subscribed_field_in_course_serializer(self):
        """Поле is_subscribed равно False, если подписки нет."""
        self.client.force_authenticate(user=self.user)

        response = self.client.get(f"/materials/courses/{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("is_subscribed", response.data)
        self.assertFalse(response.data["is_subscribed"])
