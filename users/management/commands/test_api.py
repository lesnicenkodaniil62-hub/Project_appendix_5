from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from rest_framework import status
from rest_framework.test import APIClient

from materials.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    help = "Комплексное тестирование всех эндпоинтов проекта (feature_1, feature_2, feature_3)"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = APIClient()
        self.passed = 0
        self.failed = 0
        self.total = 0

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить все тестовые данные",
        )
        parser.add_argument(
            "--feature",
            type=int,
            choices=[1, 2, 3],
            help="Тестировать только конкретную фичу (1, 2 или 3)",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_data()
            return

        feature = options.get("feature")
        self.stdout.write(self.style.SUCCESS("\n🚀 НАЧАЛО ТЕСТИРОВАНИЯ API\n"))
        self.stdout.write("=" * 60)

        # Создаём тестовые данные
        self._setup_test_data()

        # Тестируем все фичи или выбранную
        if feature is None or feature == 1:
            self._test_feature_1()
        if feature is None or feature == 2:
            self._test_feature_2()
        if feature is None or feature == 3:
            self._test_feature_3()

        # Выводим статистику
        self._print_summary()

    def _assert(self, condition: bool, test_name: str, details: str = ""):
        """Проверяет условие и выводит результат."""
        self.total += 1
        if condition:
            self.passed += 1
            self.stdout.write(self.style.SUCCESS(f"  ✅ {test_name}"))
        else:
            self.failed += 1
            self.stdout.write(self.style.ERROR(f"  ❌ {test_name}"))
            if details:
                self.stdout.write(self.style.WARNING(f"     {details}"))

    def _setup_test_data(self):
        """Создаёт тестовых пользователей и данные."""
        self.stdout.write(self.style.SUCCESS("\n📦 Подготовка тестовых данных..."))

        # Создаём группу "Модераторы"
        moderator_group, _ = Group.objects.get_or_create(name="Модераторы")

        # Создаём обычного пользователя
        self.user1, created = User.objects.get_or_create(
            email="user1@test.com", defaults={"first_name": "Обычный", "last_name": "Пользователь1", "is_active": True}
        )
        if created:
            self.user1.set_password("testpass123")
            self.user1.save()

        # Создаём второго обычного пользователя (для тестов "чужой профиль")
        self.user2, created = User.objects.get_or_create(
            email="user2@test.com", defaults={"first_name": "Обычный", "last_name": "Пользователь2", "is_active": True}
        )
        if created:
            self.user2.set_password("testpass123")
            self.user2.save()

        # Создаём модератора
        self.moderator, created = User.objects.get_or_create(
            email="moderator@test.com",
            defaults={"first_name": "Модератор", "last_name": "Тестовый", "is_active": True},
        )
        if created:
            self.moderator.set_password("testpass123")
            self.moderator.save()
        self.moderator.groups.add(moderator_group)

        # Создаём курс и урок для user1
        self.course1, _ = Course.objects.get_or_create(
            id=100,
            defaults={
                "title": "Тестовый курс user1",
                "description": "Описание",
                "owner": self.user1,
            },
        )
        self.lesson1, _ = Lesson.objects.get_or_create(
            id=100,
            defaults={
                "title": "Тестовый урок user1",
                "description": "Описание",
                "video_url": "https://test.com",
                "course": self.course1,
                "owner": self.user1,
            },
        )

        # Создаём курс и урок для user2 (для тестов "чужие объекты")
        self.course2, _ = Course.objects.get_or_create(
            id=200,
            defaults={
                "title": "Тестовый курс user2",
                "description": "Описание",
                "owner": self.user2,
            },
        )
        self.lesson2, _ = Lesson.objects.get_or_create(
            id=200,
            defaults={
                "title": "Тестовый урок user2",
                "description": "Описание",
                "video_url": "https://test.com",
                "course": self.course2,
                "owner": self.user2,
            },
        )

        # Создаём платёж
        self.payment1, _ = Payment.objects.get_or_create(
            id=100,
            defaults={
                "user": self.user1,
                "course": self.course1,
                "amount": "1000.00",
                "payment_method": "cash",
            },
        )

        self.stdout.write(self.style.SUCCESS("  ✅ Тестовые данные готовы\n"))

    def _test_feature_1(self):
        """Тесты для feature_1: кастомная модель User, CRUD курсов/уроков."""
        self.stdout.write(self.style.SUCCESS("\n🧪 ТЕСТИРОВАНИЕ FEATURE_1\n"))
        self.stdout.write("-" * 60)

        # Аутентифицируемся как user1
        self.client.force_authenticate(user=self.user1)

        # CRUD курсов
        self.stdout.write(self.style.SUCCESS("\n📚 CRUD курсов:"))
        response = self.client.get("/materials/courses/")
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "GET /materials/courses/ — список курсов",
            f"Ожидался 200, получен {response.status_code}",
        )

        response = self.client.get(f"/materials/courses/{self.course1.id}/")
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "GET /materials/courses/{id}/ — детали курса",
            f"Ожидался 200, получен {response.status_code}",
        )

        response = self.client.patch(f"/materials/courses/{self.course1.id}/", {"title": "Обновлённый курс user1"})
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "PATCH /materials/courses/{id}/ — обновление своего курса",
            f"Ожидался 200, получен {response.status_code}",
        )

        # CRUD уроков
        self.stdout.write(self.style.SUCCESS("\n📖 CRUD уроков:"))
        response = self.client.get("/materials/lessons/")
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "GET /materials/lessons/ — список уроков",
            f"Ожидался 200, получен {response.status_code}",
        )

        response = self.client.get(f"/materials/lessons/{self.lesson1.id}/")
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "GET /materials/lessons/{id}/ — детали урока",
            f"Ожидался 200, получен {response.status_code}",
        )

        response = self.client.patch(
            f"/materials/lessons/{self.lesson1.id}/update/", {"title": "Обновлённый урок user1"}
        )
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "PATCH /materials/lessons/{id}/update/ — обновление своего урока",
            f"Ожидался 200, получен {response.status_code}",
        )

    def _test_feature_2(self):
        """Тесты для feature_2: lessons_count, платежи, фильтрация, профиль с платежами."""
        self.stdout.write(self.style.SUCCESS("\n🧪 ТЕСТИРОВАНИЕ FEATURE_2\n"))
        self.stdout.write("-" * 60)

        self.client.force_authenticate(user=self.user1)

        # lessons_count в CourseSerializer
        self.stdout.write(self.style.SUCCESS("\n🔢 lessons_count:"))
        response = self.client.get(f"/materials/courses/{self.course1.id}/")
        if response.status_code == 200:
            has_lessons_count = "lessons_count" in response.data
            self._assert(
                has_lessons_count, "Поле lessons_count присутствует в ответе курса", "Поле не найдено в ответе"
            )
            if has_lessons_count:
                self._assert(
                    isinstance(response.data["lessons_count"], int),
                    "lessons_count — целое число",
                    f"Тип: {type(response.data['lessons_count'])}",
                )
        else:
            self._assert(False, "lessons_count", f"Ошибка запроса: {response.status_code}")

        # Вложенные уроки
        self.stdout.write(self.style.SUCCESS("\n📦 Вложенные уроки:"))
        response = self.client.get(f"/materials/courses/{self.course1.id}/")
        if response.status_code == 200:
            has_lessons = "lessons" in response.data
            self._assert(has_lessons, "Поле lessons (вложенные уроки) присутствует", "Поле не найдено")
        else:
            self._assert(False, "Вложенные уроки", f"Ошибка: {response.status_code}")

        # Фильтрация и сортировка платежей
        self.stdout.write(self.style.SUCCESS("\n🔍 Фильтрация и сортировка платежей:"))
        response = self.client.get("/users/payments/")
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "GET /users/payments/ — список платежей",
            f"Ожидался 200, получен {response.status_code}",
        )

        response = self.client.get("/users/payments/?course=" + str(self.course1.id))
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "Фильтр по курсу (?course=)",
            f"Ожидался 200, получен {response.status_code}",
        )

        response = self.client.get("/users/payments/?payment_method=cash")
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "Фильтр по способу оплаты (?payment_method=cash)",
            f"Ожидался 200, получен {response.status_code}",
        )

        response = self.client.get("/users/payments/?ordering=payment_date")
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "Сортировка по возрастанию (?ordering=payment_date)",
            f"Ожидался 200, получен {response.status_code}",
        )

        response = self.client.get("/users/payments/?ordering=-payment_date")
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "Сортировка по убыванию (?ordering=-payment_date)",
            f"Ожидался 200, получен {response.status_code}",
        )

        # Профиль с платежами
        self.stdout.write(self.style.SUCCESS("\n💰 Профиль с платежами:"))
        response = self.client.get(f"/users/users/{self.user1.id}/profile/")
        if response.status_code == 200:
            has_payments = "payments" in response.data
            self._assert(has_payments, "Поле payments присутствует в профиле", "Поле не найдено")
        else:
            self._assert(False, "Профиль с платежами", f"Ошибка: {response.status_code}")

    def _test_feature_3(self):
        """Тесты для feature_3: регистрация, JWT, permissions, модераторы, профили."""
        self.stdout.write(self.style.SUCCESS("\n🧪 ТЕСТИРОВАНИЕ FEATURE_3\n"))
        self.stdout.write("-" * 60)

        # Регистрация
        self.stdout.write(self.style.SUCCESS("\n📝 Регистрация:"))
        self.client.force_authenticate(user=None)  # Сбрасываем аутентификацию
        response = self.client.post(
            "/users/register/",
            {
                "email": "newuser@test.com",
                "password": "testpass123",
                "password_confirm": "testpass123",
                "first_name": "Новый",
                "last_name": "Пользователь",
            },
        )
        self._assert(
            response.status_code == status.HTTP_201_CREATED,
            "POST /users/register/ — успешная регистрация",
            f"Ожидался 201, получен {response.status_code}. Ответ: {response.data if hasattr(response, 'data') else response.content}",
        )

        # Проверка уникальности email
        response = self.client.post(
            "/users/register/",
            {
                "email": "user1@test.com",  # Уже существует
                "password": "testpass123",
                "password_confirm": "testpass123",
                "first_name": "Дубликат",
                "last_name": "Пользователь",
            },
        )
        self._assert(
            response.status_code == status.HTTP_400_BAD_REQUEST,
            "Регистрация с существующим email → 400",
            f"Ожидался 400, получен {response.status_code}",
        )

        # JWT токены
        self.stdout.write(self.style.SUCCESS("\n🔑 JWT токены:"))
        response = self.client.post("/api/token/", {"email": "user1@test.com", "password": "testpass123"})
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "POST /api/token/ — получение access/refresh",
            f"Ожидался 200, получен {response.status_code}",
        )
        if response.status_code == 200:
            self._assert(
                "access" in response.data and "refresh" in response.data,
                "Ответ содержит access и refresh токены",
                f"Ключи: {list(response.data.keys())}",
            )
            refresh_token = response.data.get("refresh")

            # Обновление токена
            if refresh_token:
                response = self.client.post("/api/token/refresh/", {"refresh": refresh_token})
                self._assert(
                    response.status_code == status.HTTP_200_OK,
                    "POST /api/token/refresh/ — обновление токена",
                    f"Ожидался 200, получен {response.status_code}",
                )

        # Аутентификация обязательна
        self.stdout.write(self.style.SUCCESS("\n🔒 Обязательная аутентификация:"))
        self.client.force_authenticate(user=None)
        response = self.client.get("/materials/courses/")
        self._assert(
            response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
            "GET /materials/courses/ без токена → 401/403",
            f"Ожидался 401/403, получен {response.status_code}",
        )

        # Права модератора
        self.stdout.write(self.style.SUCCESS("\n👮 Права модератора:"))
        self.client.force_authenticate(user=self.moderator)

        # Модератор НЕ может создать курс
        response = self.client.post("/materials/courses/", {"title": "Курс модератора", "description": "Тест"})
        self._assert(
            response.status_code == status.HTTP_403_FORBIDDEN,
            "Модератор НЕ может создать курс → 403",
            f"Ожидался 403, получен {response.status_code}",
        )

        # Модератор НЕ может удалить курс
        response = self.client.delete(f"/materials/courses/{self.course1.id}/")
        self._assert(
            response.status_code == status.HTTP_403_FORBIDDEN,
            "Модератор НЕ может удалить курс → 403",
            f"Ожидался 403, получен {response.status_code}",
        )

        # Модератор НЕ может создать урок
        response = self.client.post("/materials/lessons/", {"title": "Урок модератора", "course": self.course1.id})
        self._assert(
            response.status_code == status.HTTP_403_FORBIDDEN,
            "Модератор НЕ может создать урок → 403",
            f"Ожидался 403, получен {response.status_code}",
        )

        # Модератор МОЖЕТ просматривать чужие курсы
        response = self.client.get(f"/materials/courses/{self.course1.id}/")
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "Модератор МОЖЕТ просматривать чужие курсы",
            f"Ожидался 200, получен {response.status_code}",
        )

        # Модератор МОЖЕТ редактировать чужие курсы
        response = self.client.patch(f"/materials/courses/{self.course1.id}/", {"title": "Обновлено модератором"})
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "Модератор МОЖЕТ редактировать чужие курсы",
            f"Ожидался 200, получен {response.status_code}",
        )

        # Автоматическое заполнение owner
        self.stdout.write(self.style.SUCCESS("\n👤 Автоматическое заполнение owner:"))
        self.client.force_authenticate(user=self.user1)
        response = self.client.post("/materials/courses/", {"title": "Новый курс user1", "description": "Тест"})
        if response.status_code == 201:
            self._assert(
                response.data.get("owner") == self.user1.id,
                "При создании курса owner = request.user",
                f"Ожидался {self.user1.id}, получен {response.data.get('owner')}",
            )
            # Удаляем созданный курс
            Course.objects.filter(id=response.data["id"]).delete()
        else:
            self._assert(False, "Создание курса для теста owner", f"Статус: {response.status_code}")

        # Доступ только к своим объектам
        self.stdout.write(self.style.SUCCESS("\n🔐 Доступ только к своим объектам:"))
        self.client.force_authenticate(user=self.user1)

        # user1 видит свой курс
        response = self.client.get("/materials/courses/")
        if response.status_code == 200:
            course_ids = [c["id"] for c in response.data]
            self._assert(
                self.course1.id in course_ids and self.course2.id not in course_ids,
                "Обычный пользователь видит ТОЛЬКО свои курсы",
                f"Виден курс user2: {self.course2.id in course_ids}",
            )
        else:
            self._assert(False, "Проверка видимости курсов", f"Статус: {response.status_code}")

        # user1 НЕ может редактировать курс user2
        response = self.client.patch(f"/materials/courses/{self.course2.id}/", {"title": "Попытка взлома"})
        self._assert(
            response.status_code == status.HTTP_404_NOT_FOUND,
            "Обычный пользователь НЕ может редактировать чужой курс → 404",
            f"Ожидался 404, получен {response.status_code}",
        )

        # Просмотр профилей
        self.stdout.write(self.style.SUCCESS("\n👀 Просмотр профилей:"))
        # Свой профиль — полный
        response = self.client.get(f"/users/users/{self.user1.id}/profile/")
        if response.status_code == 200:
            has_last_name = "last_name" in response.data
            has_payments = "payments" in response.data
            self._assert(
                has_last_name and has_payments,
                "Свой профиль содержит last_name и payments",
                f"last_name: {has_last_name}, payments: {has_payments}",
            )
        else:
            self._assert(False, "Свой профиль", f"Статус: {response.status_code}")

        # Чужой профиль — только общая информация
        response = self.client.get(f"/users/users/{self.user2.id}/profile/")
        if response.status_code == 200:
            no_last_name = "last_name" not in response.data
            no_payments = "payments" not in response.data
            self._assert(
                no_last_name and no_payments,
                "Чужой профиль БЕЗ last_name и payments",
                f"last_name: {'last_name' in response.data}, payments: {'payments' in response.data}",
            )
        else:
            self._assert(False, "Чужой профиль", f"Статус: {response.status_code}")

        # Редактирование только своего профиля
        response = self.client.patch(f"/users/users/{self.user2.id}/update/", {"first_name": "Взлом"})
        self._assert(
            response.status_code == status.HTTP_403_FORBIDDEN,
            "Нельзя редактировать чужой профиль → 403",
            f"Ожидался 403, получен {response.status_code}",
        )

        response = self.client.patch(f"/users/users/{self.user1.id}/update/", {"first_name": "Обновлено"})
        self._assert(
            response.status_code == status.HTTP_200_OK,
            "Можно редактировать свой профиль → 200",
            f"Ожидался 200, получен {response.status_code}",
        )

    def _clear_data(self):
        """Удаляет все тестовые данные."""
        self.stdout.write(self.style.WARNING("\n🗑️ Очистка тестовых данных..."))

        # Удаляем платежи
        Payment.objects.filter(id__in=[100]).delete()

        # Удаляем уроки и курсы
        Lesson.objects.filter(id__in=[100, 200]).delete()
        Course.objects.filter(id__in=[100, 200]).delete()

        # Удаляем пользователей
        User.objects.filter(
            email__in=["user1@test.com", "user2@test.com", "moderator@test.com", "newuser@test.com"]
        ).delete()

        # Удаляем группу
        Group.objects.filter(name="Модераторы").delete()

        self.stdout.write(self.style.SUCCESS("✅ Тестовые данные удалены\n"))

    def _print_summary(self):
        """Выводит итоговую статистику."""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("📊 ИТОГОВАЯ СТАТИСТИКА"))
        self.stdout.write("=" * 60)
        self.stdout.write(f"  Всего тестов: {self.total}")
        self.stdout.write(self.style.SUCCESS(f"  ✅ Пройдено: {self.passed}"))
        if self.failed > 0:
            self.stdout.write(self.style.ERROR(f"  ❌ Провалено: {self.failed}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"  ❌ Провалено: {self.failed}"))
        self.stdout.write("=" * 60)

        if self.failed == 0:
            self.stdout.write(self.style.SUCCESS("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!\n"))
        else:
            self.stdout.write(self.style.ERROR(f"\n⚠️ {self.failed} тест(ов) провалено. Проверьте логи выше.\n"))
