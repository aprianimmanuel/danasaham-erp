from __future__ import annotations

from django.apps import AppConfig


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.config.user"
    verbose_name = "user"


class UserProfile(AppConfig):
    name = "app.config.user"
    verbose_name = "UserProfile"

    def ready(self) -> None:
        pass
