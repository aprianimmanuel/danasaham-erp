from __future__ import annotations

from django.apps import AppConfig


class DttotDocConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.dttotDoc"
    verbose_name = "DTTOT Documents"

    def ready(self) -> None:
        import app.config.dttotDoc.signals  # noqa: F401
