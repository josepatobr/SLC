from django.conf import settings
from celery import Celery
import os


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("SLC")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()