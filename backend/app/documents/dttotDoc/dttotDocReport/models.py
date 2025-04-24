from __future__ import annotations

import uuid
from typing import ClassVar

from django.conf import settings  # type: ignore  # noqa: PGH003
from django.db import models  #type: ignore   # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore   # noqa: PGH003

from app.documents.models import (
    Document,  #type: ignore  # noqa: PGH003
)


class DttotDocReport(models.Model):
    dttotdoc_report_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        max_length=36,
        unique=True,
        verbose_name=_("DTTOT Doc Report ID"),
    )
    document = models.OneToOneField(
        Document,
        on_delete=models.CASCADE,
        related_name="dttotDocReport",
        related_query_name="dttotDocReport",
        null=False,
    )
    created_date = models.DateTimeField(
        _("DTTOT Doc Report Instruction Created Date"),
        auto_now_add=True,
    )
    updated_date = models.DateTimeField(_("DTTOT Report Date"), auto_now=True)
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Updated by User"),
        related_name="updated_dttotDocReports",
        related_query_name="updated_dttotDocReport",
        null=True,
    )
    status_doc = models.CharField(  # noqa: DJ001
        _("Status Doc Processing"),
        max_length=50,
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "dttotdoc_report"
        verbose_name = _("DTTOT Document Report")
        verbose_name_plural = _("DTTOT Document Reports")
        ordering: ClassVar = ["-created_date"]
        indexes: ClassVar = [
            models.Index(fields=["document"], name="idx_dttot_document"),
            models.Index(fields=["status_doc"], name="idx_dttot_status_doc"),
        ]


    def __str__(self) -> str:
        return f"{self.dttotdoc_report_id} - {self.document} - {self.created_date}"

