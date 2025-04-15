from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class DttotDocConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.dttotDoc"
    verbose_name = "DTTOT Documents"

    def ready(self) -> None:
        import app.dttotDoc.signals  #type: ignore # noqa: PGH003, F401
