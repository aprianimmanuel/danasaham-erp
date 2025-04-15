from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.user"
    verbose_name = "User"

    def ready(self) -> None:
        pass


class UserProfile(AppConfig):
    name = "app.user_profile"
    verbose_name = "UserProfile"

    def ready(self) -> None:
        pass
