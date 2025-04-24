from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class DttotDocReportPersonalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.documents.dttotDoc.dttotDocReportPersonal"
    verbose_name = "DTTOT Doc Report Personal"
    verbose_name_plural = "DTTOT Doc Report Personals"

    def ready(self) -> None:
        import app.documents.dttotDoc.dttotDocReportPersonal.tasks  #type: ignore # noqa: PGH003, F401
