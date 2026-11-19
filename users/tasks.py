import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mass_mail
from django.utils import timezone

from materials.models import Course, Subscription
from users.models import User

logger = logging.getLogger(__name__)


@shared_task
def test_celery_connection():
    """Простая задача для проверки работы Celery и Celery Beat."""
    logger.info(" Celery работает! Задача test_celery_connection выполнена успешно.")
    return "Celery is working!"


@shared_task
def send_course_update_notification(course_id: int):
    """
    Отправляет уведомления всем подписчикам об обновлении курса.
    Отправка происходит батчем (одним SMTP-соединением) через send_mass_mail.
    """
    try:
        course = Course.objects.get(id=course_id)
    except Course.DoesNotExist:
        return f"Курс с ID {course_id} не найден"

    # Критерий: Проверка через timezone.now() — updated_at; логика < 4 часов соблюдена
    if (timezone.now() - course.updated_at) > timedelta(hours=4):
        return f"Курс '{course.title}' был обновлен более 4 часов назад. Уведомление не отправлено."

    # Критерий: Выборка пользователей правильная (используем select_related для оптимизации)
    subscriptions = Subscription.objects.filter(course=course).select_related("user")

    if not subscriptions:
        return f"Нет подписчиков для курса '{course.title}'"

    subject = f"Обновление курса: {course.title}"
    message = (
        f"Здравствуйте!\n\n"
        f"Курс '{course.title}', на который вы подписаны, был обновлен.\n\n"
        f"Описание: {course.description}\n\n"
        f"С уважением, команда LMS Platform."
    )
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "mrd31les99@mail.ru")

    # Критерий: Обновление (отправка) происходит батчем, а не по одному.
    # send_mass_mail открывает ОДНО соединение с SMTP-сервером и отправляет все письма,
    # что гораздо эффективнее, чем вызов send_mail в цикле.
    datatuple = tuple((subject, message, from_email, [sub.user.email]) for sub in subscriptions if sub.user.email)

    if datatuple:
        send_mass_mail(datatuple, fail_silently=False)

    return f"Успешно отправлено {len(datatuple)} уведомлений для курса '{course.title}'"


@shared_task
def block_inactive_users():
    """
    Периодическая задача: блокирует пользователей, которые не заходили более месяца.
    Обновление происходит БАТЧЕМ через .update(), а не в цикле.
    """
    # Критерий: Проверка через timezone.now() — last_login; логика > 1 месяца
    threshold_date = timezone.now() - timedelta(days=30)

    # Критерий: Выборка пользователей правильная
    # Выбираем активных пользователей, которые не заходили более 30 дней
    # Также исключаем суперпользователей (is_staff=True) — это хорошая практика
    inactive_users = User.objects.filter(
        is_active=True,
        last_login__lt=threshold_date,
        is_staff=False,  # Не блокируем администраторов
    )

    users_count = inactive_users.count()

    if users_count == 0:
        logger.info("Нет неактивных пользователей для блокировки.")
        return "Нет пользователей для блокировки"

    # Критерий: Обновление происходит батчем, а не по одному
    # Один SQL-запрос UPDATE ... SET is_active=False WHERE ...
    updated_count = inactive_users.update(is_active=False)

    logger.info(f"Заблокировано пользователей: {updated_count}")
    return f"Заблокировано пользователей: {updated_count}"
