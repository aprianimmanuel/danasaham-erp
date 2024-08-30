from __future__ import annotations

from django.apps import AppConfig


class dttotDocReportConfig(AppConfig):  # noqa: N801
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.dttotDocReport"
    verbose_name = "DTTOT Doc Reports"

    def ready(self) -> None:
        import app.config.dttotDocReport.tasks
