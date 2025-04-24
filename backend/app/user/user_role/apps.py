from __future__ import annotations

from django.apps import AppConfig  # type: ignore  # noqa: PGH003


class UserRoleConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.user.user_role"
    verbose_name = "User Role"
    verbose_name_plural = "User Roles"

    def ready(self):
        pass
