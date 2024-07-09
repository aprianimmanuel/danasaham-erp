from __future__ import annotations

from django.apps import AppConfig


class DsbUserCorporateCOnfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.dsb_user_corporate"

    def ready(self) -> None:
        import app.config.dsb_user_corporate.signals