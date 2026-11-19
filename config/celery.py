import os
from celery import Celery

# Указываем Django использовать настройки из config.settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Создаем экземпляр приложения Celery
app = Celery('config')

# Загружаем настройки Celery из Django settings, используя префикс 'CELERY_'
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически обнаруживаем задачи во всех установленных приложениях Django
app.autodiscover_tasks()