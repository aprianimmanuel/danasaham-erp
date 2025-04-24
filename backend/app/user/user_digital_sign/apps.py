from __future__ import annotations

from django.apps import AppConfig  # type: ignore  # noqa: PGH003


class UserDigitalSignConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.user.user_digital_sign"
    verbose_name = "User Digital Sign"
    verbose_name_plural = "User Digital Signs"

    def ready(self) -> None:
        pass
