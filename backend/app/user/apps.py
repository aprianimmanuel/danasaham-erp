from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class UserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.user"
    verbose_name = "user"

