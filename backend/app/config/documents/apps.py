from __future__ import annotations

from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.documents"
    verbose_name = "Documents"

    def ready(self) -> None:
        import app.config.documents.signals  # noqa
