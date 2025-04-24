from __future__ import annotations

import uuid

from django.conf import settings  # type: ignore  # noqa: PGH003
from django.db import models  # type: ignore  # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore  # noqa: PGH003


class UserDigitalSign(models.Model):
    digital_sign_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("Digital Sign ID"),
        unique=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="digital_sign",
        related_query_name="digital_sign",
    )
    created_date = models.DateTimeField(auto_now_add=True, editable=False)
    updated_date = models.DateTimeField(auto_now=True, editable=True)
    signature_barcode = models.FileField(
        upload_to="user_digital_signs/",
        null=True,
        blank=True,
        verbose_name=_("Digital Signature File"),
    )

    class Meta:
        db_table = "user_digital_sign"
        verbose_name = _("user_digital_sign")
        verbose_name_plural = _("user_digital_signs")

    def __str__(self) -> str:
        return f"{self.user.username} digital sign"

