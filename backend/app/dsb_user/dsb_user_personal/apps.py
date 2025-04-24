from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class DsbUserPersonalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.dsb_user.dsb_user_personal"
    verbose_name = "DSB User Personal"
    verbose_name_plural = "DSB User Personals"

    def ready(self) -> None:
        import app.dsb_user.dsb_user_personal.tasks  #type: ignore # noqa: PGH003, F401
