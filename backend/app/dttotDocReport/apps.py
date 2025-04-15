from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class dttotDocReportConfig(AppConfig):  # noqa: N801
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.dttotDocReport"
    verbose_name = "DTTOT Doc Reports"

    def ready(self) -> None:
        import app.dttotDocReport.tasks  #type: ignore # noqa: PGH003, F401
