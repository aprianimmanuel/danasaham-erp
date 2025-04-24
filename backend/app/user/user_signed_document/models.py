from __future__ import annotations

import uuid

from django.db import models  # type: ignore  # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore  # noqa: PGH003


class UserSignedDocument(models.Model):
    signed_document_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("Signed Document ID"),
        unique=True,
    )
    user_key = models.UUIDField(
        verbose_name=_("User Key ID"),
        null=True,
        blank=True,
    )
    document_id = models.UUIDField(
        verbose_name=_("Document ID"),
        null=True,
        blank=True,
    )
    is_signed = models.BooleanField(default=False, blank=True, null=True, editable=False)
    signed_at = models.DateTimeField(auto_now_add=True, blank=True, null=True, editable=False)

    class Meta:
        db_table = "user_signed_document"
        verbose_name = _("user_signed_document")
        verbose_name_plural = _("user_signed_documents")

    def __str__(self) -> str:
        return str(self.signed_document_id)
