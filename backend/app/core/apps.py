from __future__ import annotations

from django.apps import AppConfig  #type: ignore  # noqa: PGH003


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.core"
    verbose_name = "Core"
