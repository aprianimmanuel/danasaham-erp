from __future__ import annotations

from django.apps import AppConfig  # type: ignore  # noqa: PGH003


class DsbUserConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.dsb_user"
