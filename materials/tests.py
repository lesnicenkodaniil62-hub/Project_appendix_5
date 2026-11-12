from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import Payment, User

from .models import Course, Lesson, Subscription


class UserRegistrationTests(APITestCase):
    """Тесты регистрации пользователей."""

    def test_register_user_success(self):
        """Успешная регистрация нового пользователя."""
        data = {
            "email": "newuser@test.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
            "first_name": "Новый",
            "last_name": "Пользователь",
        }
        response = self.client.post("/users/register/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email="newuser@test.com").exists())

    def test_register_user_duplicate_email(self):
        """Регистрация с существующим email возвращает ошибку."""
        User.objects.create_user(email="existing@test.com", password="testpass123")
        data = {
            "email": "existing@test.com",
            "password": "testpass123",
            "password_confirm": "testpass123",
        }
        response = self.client.post("/users/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_user_password_mismatch(self):
        """Регистрация с несовпадающими паролями возвращает ошибку."""
        data = {
            "email": "user@test.com",
            "password": "testpass123",
            "password_confirm": "differentpass",
        }
        response = self.client.post("/users/register/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class JWTTokenTests(APITestCase):
    """Тесты JWT токенов."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )

    def test_obtain_token(self):
        """Получение access/refresh токенов."""
        response = self.client.post(
            "/api/token/",
            {"email": "user@test.com", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_refresh_token(self):
        """Обновление access токена."""
        # Сначала получаем токены
        response = self.client.post(
            "/api/token/",
            {"email": "user@test.com", "password": "testpass123"},
        )
        refresh_token = response.data["refresh"]

        # Обновляем access токен
        response = self.client.post(
            "/api/token/refresh/",
            {"refresh": refresh_token},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)


class UserCRUDTests(APITestCase):
    """Тесты CRUD операций для пользователей."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
            first_name="Тестовый",
            last_name="Пользователь",
        )

    def test_get_users_list(self):
        """Авторизованный пользователь может получить список пользователей."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/users/users/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_users_list_without_auth(self):
        """Неавторизованный пользователь не может получить список."""
        response = self.client.get("/users/users/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserProfileTests(APITestCase):
    """Тесты профилей пользователей."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
            first_name="Тестовый",
            last_name="Пользователь",
        )
        self.user2 = User.objects.create_user(
            email="user2@test.com",
            password="testpass123",
            first_name="Второй",
            last_name="Пользователь",
        )

    def test_get_own_profile_with_payments(self):
        """Свой профиль содержит last_name и payments."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/users/users/{self.user.id}/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("last_name", response.data)
        self.assertIn("payments", response.data)

    def test_get_other_profile_without_sensitive_data(self):
        """Чужой профиль не содержит last_name и payments."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/users/users/{self.user2.id}/profile/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("last_name", response.data)
        self.assertNotIn("payments", response.data)

    def test_update_own_profile(self):
        """Можно редактировать свой профиль."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/users/users/{self.user.id}/update/",
            {"first_name": "Обновлённый"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_other_profile_forbidden(self):
        """Нельзя редактировать чужой профиль."""
        self.client.force_authenticate(user=self.user)
        response = self.client.patch(
            f"/users/users/{self.user2.id}/update/",
            {"first_name": "Взлом"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PaymentTests(APITestCase):
    """Тесты платежей."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание",
            owner=self.user,
        )
        self.payment = Payment.objects.create(
            user=self.user,
            course=self.course,
            amount="1000.00",
            payment_method="cash",
        )

    def test_get_payments_list(self):
        """Авторизованный пользователь может получить список платежей."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/users/payments/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_payments_by_course(self):
        """Фильтрация платежей по курсу."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/users/payments/?course={self.course.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_payments_by_payment_method(self):
        """Фильтрация платежей по способу оплаты."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/users/payments/?payment_method=cash")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_order_payments_by_date(self):
        """Сортировка платежей по дате."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/users/payments/?ordering=payment_date")
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class CourseCRUDTests(APITestCase):
    """Тесты CRUD операций для курсов."""

    def setUp(self):
        self.moderator_group = Group.objects.create(name="Модераторы")
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )
        self.moderator = User.objects.create_user(
            email="moderator@test.com",
            password="testpass123",
        )
        self.moderator.groups.add(self.moderator_group)
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание",
            owner=self.user,
        )

    def test_create_course_by_user(self):
        """Обычный пользователь может создать курс."""
        self.client.force_authenticate(user=self.user)
        data = {"title": "Новый курс", "description": "Описание"}
        response = self.client.post("/materials/courses/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_course_by_moderator_forbidden(self):
        """Модератор НЕ может создать курс."""
        self.client.force_authenticate(user=self.moderator)
        data = {"title": "Курс модератора", "description": "Описание"}
        response = self.client.post("/materials/courses/", data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get_courses_list(self):
        """Авторизованный пользователь может получить список курсов."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/materials/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_course_detail(self):
        """Получение деталей курса."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/materials/courses/{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("lessons_count", response.data)
        self.assertIn("is_subscribed", response.data)

    def test_update_course_by_owner(self):
        """Владелец может обновить свой курс."""
        self.client.force_authenticate(user=self.user)
        data = {"title": "Обновлённый курс"}
        response = self.client.patch(f"/materials/courses/{self.course.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_course_by_moderator(self):
        """Модератор может обновить любой курс."""
        self.client.force_authenticate(user=self.moderator)
        data = {"title": "Обновлено модератором"}
        response = self.client.patch(f"/materials/courses/{self.course.id}/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_course_by_owner(self):
        """Владелец может удалить свой курс."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/materials/courses/{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_course_by_moderator_forbidden(self):
        """Модератор НЕ может удалить курс."""
        self.client.force_authenticate(user=self.moderator)
        response = self.client.delete(f"/materials/courses/{self.course.id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class LessonCRUDTests(APITestCase):
    """Тесты CRUD операций для уроков."""

    def setUp(self):
        self.moderator_group = Group.objects.create(name="Модераторы")
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )
        self.moderator = User.objects.create_user(
            email="moderator@test.com",
            password="testpass123",
        )
        self.moderator.groups.add(self.moderator_group)
        self.user2 = User.objects.create_user(
            email="user2@test.com",
            password="testpass123",
        )
        self.course = Course.objects.create(
            title="Тестовый курс",
            description="Описание",
            owner=self.user,
        )
        self.lesson = Lesson.objects.create(
            title="Тестовый урок",
            description="Описание",
            video_url="https://www.youtube.com/watch?v=test",
            course=self.course,
            owner=self.user,
        )

    def test_create_lesson_by_user(self):
        """Обычный пользователь может создать урок."""
        self.client.force_authenticate(user=self.user)
        data = {
            "title": "Новый урок",
            "video_url": "https://www.youtube.com/watch?v=new",
            "course": self.course.id,
        }
        response = self.client.post("/materials/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_lesson_by_moderator_forbidden(self):
        """Модератор НЕ может создать урок."""
        self.client.force_authenticate(user=self.moderator)
        data = {
            "title": "Урок модератора",
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

    def test_get_lesson_detail_by_owner(self):
        """Владелец может получить детали своего урока."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/materials/lessons/{self.lesson.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_lesson_by_owner(self):
        """Владелец может обновить свой урок."""
        self.client.force_authenticate(user=self.user)
        data = {"title": "Обновлённый урок"}
        response = self.client.patch(f"/materials/lessons/{self.lesson.id}/update/", data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_lesson_by_owner(self):
        """Владелец может удалить свой урок."""
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(f"/materials/lessons/{self.lesson.id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_lesson_by_other_user_forbidden(self):
        """Другой пользователь НЕ может удалить чужой урок."""
        self.client.force_authenticate(user=self.user2)
        response = self.client.delete(f"/materials/lessons/{self.lesson.id}/delete/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class SubscriptionTests(APITestCase):
    """Тесты функционала подписки на курс."""

    def setUp(self):
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

    def test_unsubscribe_from_course(self):
        """Пользователь может отписаться от курса."""
        Subscription.objects.create(user=self.user, course=self.course)
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            "/materials/courses/subscribe/",
            {"course_id": self.course.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "подписка удалена")

    def test_subscribe_without_auth(self):
        """Неавторизованный пользователь не может подписаться."""
        response = self.client.post(
            "/materials/courses/subscribe/",
            {"course_id": self.course.id},
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class YouTubeValidatorTests(APITestCase):
    """Тесты валидации YouTube URL."""

    def setUp(self):
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
            "video_url": "https://stepik.org/lesson/123",
            "course": self.course.id,
        }
        response = self.client.post("/materials/lessons/", data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class PaginationTests(APITestCase):
    """Тесты пагинации."""

    def setUp(self):
        self.user = User.objects.create_user(
            email="user@test.com",
            password="testpass123",
        )
        # Создаём 15 курсов
        for i in range(15):
            Course.objects.create(
                title=f"Курс {i}",
                description="Описание",
                owner=self.user,
            )

    def test_pagination_in_courses_list(self):
        """Пагинация работает для списка курсов."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/materials/courses/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("count", response.data)
        self.assertIn("next", response.data)
        self.assertIn("results", response.data)
        self.assertEqual(response.data["count"], 15)
        self.assertEqual(len(response.data["results"]), 10)  # page_size по умолчанию

    def test_pagination_with_custom_page_size(self):
        """Пагинация с пользовательским размером страницы."""
        self.client.force_authenticate(user=self.user)
        response = self.client.get("/materials/courses/?page_size=5")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 5)
