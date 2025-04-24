from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class DttotDocReportConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.documents.dttotDoc.dttotDocReport"

    def ready(self) -> None:
        import app.documents.dttotDoc.dttotDocReport.tasks  #type: ignore # noqa: PGH003, F401
