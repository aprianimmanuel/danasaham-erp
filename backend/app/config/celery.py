from __future__ import annotations

from os import getenv

# RabbitMQ settings
RABBITMQ_HOST = getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = getenv("RABBITMQ_PORT", "5672")
RABBITMQ_DEFAULT_USER = getenv("RABBITMQ_DEFAULT_USER", "rabbit")
RABBITMQ_DEFAULT_PASS = getenv("RABBITMQ_DEFAULT_PASS", "guest")
RABBITMQ_VIRTUAL_HOST = getenv("RABBITMQ_VIRTUAL_HOST", "/")
RABBITMQ_URL = getenv(
    "RABBITMQ_URL",
    f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/{RABBITMQ_VIRTUAL_HOST}",
)

# Celery configuration
CELERY_BROKER_URL = RABBITMQ_URL
CELERY_RESULT_BACKEND = getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
CELERY_TASK_ALWAYS_EAGER = getenv("CELERY_TASK_ALWAYS_EAGER", "false").lower() == "true"
CELERY_TASK_EAGER_PROPAGATES = (
    getenv("CELERY_TASK_EAGER_PROPAGATES", "false").lower() == "true"
)
CELERY_TASK_IGNORE_RESULT = (
    getenv("CELERY_TASK_IGNORE_RESULT", "false").lower() == "true"
)
CELERY_TIMEZONE = getenv("CELERY_TIMEZONE", "Asia/Jakarta")
CELERY_ENABLE_UTC = getenv("CELERY_ENABLE_UTC", "true")
CELERY_TRACK_STARTED = getenv("CELERY_TRACK_STARTED", "true")
CELERY_TASK_TRACK_STARTED = getenv("CELERY_TASK_TRACK_STARTED", "true")

# Serializer configurations
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ["json"]

# Beat scheduler configuration
CELERY_BEAT_SCHEDULER = {"django_celery_beat.schedulers:DatabaseScheduler"}
