import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def test_celery_connection():
    """Простая задача для проверки работы Celery и Celery Beat."""
    logger.info("Celery работает! Задача test_celery_connection выполнена успешно.")
    return "Celery is working!"
