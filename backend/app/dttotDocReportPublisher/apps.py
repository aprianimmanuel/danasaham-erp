from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class dttotDocReportPublisherConfig(AppConfig):  # noqa: N801
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.dttotDocReportPublisher"
    verbose_name = "DTTOT Doc Report Publisher"

    def ready(self) -> None:
        import app.dttotDocReportPublisher.tasks  #type: ignore # noqa: PGH003, F401
