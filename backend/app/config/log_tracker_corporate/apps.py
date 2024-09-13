from __future__ import annotations

from django.apps import AppConfig


class LogTrackerCorporateConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.log_tracker_corporate"

    def ready(self):
        pass
