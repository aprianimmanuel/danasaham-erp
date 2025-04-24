from __future__ import annotations

import uuid
from typing import ClassVar

from django.conf import settings  # type: ignore  # noqa: PGH003
from django.db import models  # type: ignore  # noqa: PGH003
from django.utils import timezone  # type: ignore  # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore  # noqa: PGH003


class OTPType(models.TextChoices):
    EMAIL_VERIFICATION = "EMAIL_VERIFICATION", _("Email Verification")
    WHATSAPP_REGISTRATION = "WHATSAPP_REGISTRATION", _("WhatsApp Registration")
    LOGIN_OTP = "LOGIN_OTP", _("Login OTP")


class UserOTP(models.Model):
    """Stores OTP tokens for user registration/login purposes."""

    otp_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("OTP ID"),
        unique=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_otp",
        related_query_name="user_otp",
        null=True,
        blank=True,
    )
    otp_code = models.CharField(max_length=10, blank=True)
    otp_type = models.CharField(
        max_length=100,
        choices=OTPType.choices,
        default=OTPType.LOGIN_OTP,
        blank=True,
    )
    status_used = models.CharField(max_length=20, blank=True)
    created_date = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_date = models.DateTimeField(auto_now=True, null=True, blank=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "user_otp"
        verbose_name = _("user_otp")
        verbose_name_plural = _("user_otp")
        indexes: ClassVar = [
            models.Index(fields=["otp_code", "otp_type"], name="idx_otp_code_type"),
        ]

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.otp_type} for {self.user.username}"