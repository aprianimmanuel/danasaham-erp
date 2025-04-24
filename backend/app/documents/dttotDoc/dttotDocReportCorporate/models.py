from __future__ import annotations

import uuid

from django.conf import settings  #type: ignore  # noqa: PGH003
from django.db import models  #type: ignore   # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore   # noqa: PGH003

from app.documents.dttotDoc.dttotDocReport.models import (
    DttotDocReport,  #type: ignore  # noqa: PGH003
)


class DttotDocReportCorporate(models.Model):
    dttotdoc_report = models.ForeignKey(
        DttotDocReport,
        on_delete=models.CASCADE,
        related_name="corporate_reports",
        related_query_name="corporate_report",
    )
    dttotdoc_report_corporate_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        max_length=36,
        unique=True,
        verbose_name=_("DTTOT Doc Report Corporate ID"),
    )
    created_date = models.DateTimeField(_("Entry Created Date"), auto_now_add=True)
    last_updated_date = models.DateTimeField(_("Entry Updated Date"), auto_now=True)
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Updated by User"),
        related_name="updated_dttotDoc_corporates",
        related_query_name="updated_dttotDoc_corporate",
        null=True,
    )
    dsb_user_corporate = models.CharField(
        _("Entry Corporate User that matched with similarity > 0.8"),
        max_length=255,
        blank=True,
    )
    kode_densus_corporate = models.CharField(
        _("Entry Corporate User that matched with similarity > 0.8"),
        blank=True,
        max_length=20,
    )
    score_match_similarity = models.FloatField(
        _("Similarity Score"),
        default=0.0,
    )

    class Meta:
        db_table = "dttotdoc_corporate"
        verbose_name = "DTTOT Data from User Corporate"
        verbose_name_plural = "Multi DTTOT Data from User Corporate"

    def __str__(self) -> str:
        return f"{self.dttotdoc_report} - {self.dsb_user_corporate} - {self.score_match_similarity} - {self.kode_densus_corporate}"
