from __future__ import annotations

import uuid

from django.conf import settings
from django.db import models  # type: ignore  # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore  # noqa: PGH003

from app.user.models import User


class UserKeyManagement(models.Model):
    """User Key Pair Models."""

    user_key_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("User Key ID"),
        unique=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_key_management",
        related_query_name="user_key_management",
    )
    public_key = models.TextField()
    private_key = models.TextField()
    issued_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_key_management"
        verbose_name = "User Key Management"
        verbose_name_plural = "User Key Management"

    def __str__(self) -> str:
        return f"{self.user.username} - {self.issued_at}"
