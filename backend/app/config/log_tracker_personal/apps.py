from __future__ import annotations

from django.apps import AppConfig


class LogTrackerPersonalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.log_tracker_personal"

    def ready(self):
        pass