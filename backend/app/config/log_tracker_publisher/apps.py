from __future__ import annotations

from django.apps import AppConfig


class log_tracker_publisherConfig(AppConfig):  # noqa: N801
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.log_tracker_publisher"

    def ready(self) -> None:
        pass