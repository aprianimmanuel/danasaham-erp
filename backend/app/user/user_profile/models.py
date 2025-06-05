from __future__ import annotations

import uuid

from django.conf import settings  # type: ignore  # noqa: PGH003
from django.db import models  # type: ignore  # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore  # noqa: PGH003


class UserProfile(models.Model):
    """User Profile Models."""

    profile_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        max_length=36,
        verbose_name=_("Profile ID"),
        unique=True,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        related_query_name="profile",
    )
    created_date = models.DateTimeField(auto_now=True)
    updated_date = models.DateTimeField(auto_now_add=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)


    class Meta:
        db_table = "user_profile"
        verbose_name = _("user_profile")
        verbose_name_plural = _("user_profiles")


    def __str__(self) -> str:
        return self.user.username

