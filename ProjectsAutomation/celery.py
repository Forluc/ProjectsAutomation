from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Установите модуль настроек Django по умолчанию для программы 'celery'.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ProjectsAutomation.settings')

app = Celery('ProjectsAutomation')

# Использование строки настроек Django для настройки Celery.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Загрузите задачи модуля приложения.
app.autodiscover_tasks()
