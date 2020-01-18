from celery import Celery
from django.conf import settings


app = Celery("streamkit")
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()