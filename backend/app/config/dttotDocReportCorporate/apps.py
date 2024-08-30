from __future__ import annotations

from django.apps import AppConfig


class dttotDocReportCorporateConfig(AppConfig):  # noqa: N801
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.dttotDocReportCorporate"
    verbose_name = "DTTOT Doc Report Corporate"

    def ready(self) -> None:
        import app.config.dttotDocReportCorporate.tasks