from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class DttotDocReportCorporateConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.documents.dttotDoc.dttotDocReportCorporate"
    verbose_name = "DTTOT Doc Report Corporate"
    verbose_name_plural = "DTTOT Doc Report Corporates"

    def ready(self) -> None:
        import app.documents.dttotDoc.dttotDocReportCorporate.tasks  #type: ignore # noqa: PGH003, F401
