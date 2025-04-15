from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class dttotDocReportCorporateConfig(AppConfig):  # noqa: N801
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.dttotDocReportCorporate"
    verbose_name = "DTTOT Doc Report Corporate"

    def ready(self) -> None:
        import app.dttotDocReportCorporate.tasks  #type: ignore # noqa: PGH003, F401
