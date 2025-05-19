from __future__ import annotations

import uuid
from typing import Any

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class UserSessionType(models.TextChoices):
    LOGIN = "LOGIN", _("Login")
    LOGOUT = "LOGOUT", _("Logout")
    DTTOTREPORT = "DTTOTREPORT", _("DTTOT Report")


class UserSessionStatus(models.TextChoices):
    SUCCESS = "ACTIVE", _("Active")
    FAILED = "INACTIVE", _("Inactive")
    ONHOLD = "ONHOLD", _("Onhold")



class UserSession(models.model):
    user_session_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("User Session ID"),
        unique=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_session",
        related_query_name="user_session",
    )
    session_name = models.CharField(
        max_length=100,
        choices=UserSessionType.choices,
        default="",
        blank=True,
    )
    session_status = models.CharField(
        max_length=100,
        choices=UserSessionStatus.choices,
        default="",
        blank=True,
    )
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_session"
        verbose_name = _("User Session")
        verbose_name_plural = _("User Sessions")

    def __str__(self):
        return str(self.user_session_id)