from __future__ import annotations

from django.apps import AppConfig


class dttotDocReportPersonalConfig(AppConfig):  # noqa: N801
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.dttotDocReportPersonal"
    verbose_name = "DTTOT Doc Report Personal"

    def ready(self) -> None:
        import app.config.dttotDocReportPersonal.tasks
