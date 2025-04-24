from __future__ import annotations

from django.apps import AppConfig  # type: ignore  # noqa: PGH003


class UserKeyManagementConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.user.user_key_management"
    verbose_name = "User Key Management"
    verbose_name_plural = "User Key Management"

    def ready(self) -> None:
        pass
