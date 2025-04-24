from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class DttotDocReportPublisherConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.documents.dttotDoc.dttotDocReportPublisher"
    verbose_name = "DTTOT Doc Report Publisher"

    def ready(self) -> None:
        import app.documents.dttotDoc.dttotDocReportPublisher.tasks  #type: ignore # noqa: PGH003, F401
