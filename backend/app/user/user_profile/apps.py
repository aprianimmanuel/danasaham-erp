from __future__ import annotations

from django.apps import AppConfig  # type: ignore  # noqa: PGH003


class UserProfileConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.user.user_profile"
    verbose_name = "User Profile"
    verbose_name_plural = "User Profiles"

    def ready(self) -> None:
        pass
