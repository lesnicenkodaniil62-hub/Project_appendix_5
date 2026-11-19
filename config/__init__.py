# Это гарантирует, что приложение Celery всегда импортируется,
# когда запускается Django, чтобы shared_task использовал этот экземпляр.
from .celery import app as celery_app

__all__ = ('celery_app',)