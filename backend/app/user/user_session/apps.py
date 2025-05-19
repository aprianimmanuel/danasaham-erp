from __future__ import annotations

from django.apps import AppConfig  # type: ignore  # noqa: PGH003


class UserSessionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.user.user_session"
    verbose_name = "User Session"
    verbose_name_plural = "User Sessions"