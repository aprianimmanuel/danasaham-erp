from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class DocumentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.documents"

    def ready(self):
        import app.documents.signals
        import app.documents.dttotDoc.signals