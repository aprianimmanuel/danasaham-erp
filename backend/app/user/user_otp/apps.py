from __future__ import annotations

from django.apps import AppConfig  # type: ignore  # noqa: PGH003


class UserOTPConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.user.user_otp"
    verbose_name = "User OTP"
    verbose_name_plural = "User OTP"

    def ready(self) -> None:
        import app.user.user_otp.signals
