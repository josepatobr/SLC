from celery import Celery
import os
from django.conf import settings


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("SLC", broker=settings("CELERY_BROKER_URL"))
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
