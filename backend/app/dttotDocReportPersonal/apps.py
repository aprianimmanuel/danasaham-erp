from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class dttotDocReportPersonalConfig(AppConfig):  # noqa: N801
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.dttotDocReportPersonal"
    verbose_name = "DTTOT Doc Report Personal"

    def ready(self) -> None:
        import app.dttotDocReportPersonal.tasks  #type: ignore # noqa: PGH003, F401
