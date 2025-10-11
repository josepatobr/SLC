from celery import Celery
import os
from dotenv import load_dotenv

load_dotenv()


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('SLC', broker=os.getenv("CELERY_BROKER_URL"))
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()