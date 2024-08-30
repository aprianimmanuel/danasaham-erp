from __future__ import annotations

from django.apps import AppConfig


class dttotDocReportPublisherConfig(AppConfig):  # noqa: N801
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.dttotDocReportPublisher"
    verbose_name = "DTTOT Doc Report Publisher"

    def ready(self) -> None:
        import app.config.dttotDocReportPublisher.tasks