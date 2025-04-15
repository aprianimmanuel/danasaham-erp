from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class DocumentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.documents"
    verbose_name = "Documents"

    def ready(self) -> None:
        import app.documents.signals  #type: ignore # noqa: PGH003, F401
