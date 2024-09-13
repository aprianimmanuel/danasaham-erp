from __future__ import annotations

from django.apps import AppConfig


class log_tracker_publisherConfig(AppConfig):  # noqa: N801
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.log_tracker_publisher"
    verbose_name = "Log Tracker Publisher"

    def ready(self) -> None:
        import app.config.log_tracker_publisher.signals  # noqa: F401