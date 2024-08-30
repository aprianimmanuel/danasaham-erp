from __future__ import annotations

from django.apps import AppConfig


class DsbUserPublisherConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.dsb_user_publisher"

    def ready(self) -> None:
        pass
