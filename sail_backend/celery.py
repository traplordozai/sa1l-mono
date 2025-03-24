import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sail_backend.settings")

app = Celery("sail_backend")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()