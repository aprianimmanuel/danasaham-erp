from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class DsbUserCorporateConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.dsb_user_corporate"
    verbose_name = "DSB User Corporate"

    def ready(self) -> None:
        import app.dsb_user_corporate.tasks  #type: ignore # noqa: PGH003, F401
