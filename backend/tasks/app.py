from __future__ import annotations

import logging
import os

from celery import Celery, Task
from django.conf import settings


logger = logging.getLogger(__name__)


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.config.settings")

celery_app = Celery("app")

# Include the Celery settings from Django settings
celery_app.config_from_object("django.conf:settings", namespace="CELERY")

# Explicitly set the broker and backend
celery_app.conf.broker_url = settings.CELERY_BROKER_URL
celery_app.conf.result_backend = settings.CELERY_RESULT_BACKEND

# Include task modules from all registered Django app configs.
celery_app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@celery_app.task(bind=True)
def debug_task(self: Task) -> None:
    logger.debug(f"Request: {self.request!r}")
