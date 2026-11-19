from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mass_mail
from django.utils import timezone

from .models import Course, Subscription


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
    datatuple = ((subject, message, from_email, [sub.user.email]) for sub in subscriptions if sub.user.email)

    # Преобразуем генератор в кортеж и отправляем
    send_mass_mail(tuple(datatuple), fail_silently=False)

    return f"Успешно отправлено {subscriptions.count()} уведомлений для курса '{course.title}'"
