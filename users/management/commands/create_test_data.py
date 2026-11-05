from typing import Any

from django.core.management.base import BaseCommand

from materials.models import Course, Lesson
from users.models import Payment, User


class Command(BaseCommand):
    help = "Создает тестовые данные (пользователь, курс, урок, платежи) или очищает их"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Удалить все созданные тестовые данные",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self._clear_data()
        else:
            self._create_data()

    def _create_data(self):
        # 1. Создаем пользователя (ORM сам проставит date_joined и захеширует пароль)
        user, user_created = User.objects.get_or_create(
            email="test@example.com",
            defaults={
                "first_name": "Тест",
                "last_name": "Пользователь",
                "phone": "+79990000000",
                "city": "Москва",
                "is_active": True,
            },
        )
        if user_created:
            user.set_password("testpass123")
            user.save()
            self.stdout.write(self.style.SUCCESS("Пользователь создан"))

        # 2. Создаем курс
        course, course_created = Course.objects.get_or_create(
            id=1,
            defaults={
                "title": "Курс по Python",
                "description": "Изучаем Python с нуля",
                "owner": user,
            },
        )
        if course_created:
            self.stdout.write(self.style.SUCCESS("Курс создан"))

        # 3. Создаем урок
        lesson, lesson_created = Lesson.objects.get_or_create(
            id=1,
            defaults={
                "title": "Урок 1: Введение",
                "description": "Основы синтаксиса",
                "video_url": "https://youtube.com/watch?v=test",
                "course": course,
            },
        )
        if lesson_created:
            self.stdout.write(self.style.SUCCESS("Урок создан"))

        # 4. Создаем платежи с явной типизацией
        payments_data: list[dict[str, Any]] = [
            {"user": user, "course": course, "lesson": None, "amount": "5000.00", "payment_method": "transfer"},
            {"user": user, "course": None, "lesson": lesson, "amount": "1500.00", "payment_method": "cash"},
        ]

        created_count = 0
        for data in payments_data:
            Payment.objects.get_or_create(**data)
            created_count += 1

        self.stdout.write(self.style.SUCCESS(f"Создано/обновлено {created_count} платежей"))

    def _clear_data(self):
        # Самоочистка: удаляем платежи, уроки, курсы и тестового пользователя
        Payment.objects.all().delete()
        Lesson.objects.filter(id=1).delete()
        Course.objects.filter(id=1).delete()
        User.objects.filter(email="test@example.com").delete()
        self.stdout.write(self.style.WARNING("Тестовые данные успешно удалены"))
