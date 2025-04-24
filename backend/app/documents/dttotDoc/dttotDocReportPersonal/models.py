from __future__ import annotations

import uuid

from django.conf import settings  #type: ignore  # noqa: PGH003
from django.db import models  #type: ignore   # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore   # noqa: PGH003

from app.documents.dttotDoc.dttotDocReport.models import (
    DttotDocReport,  #type: ignore  # noqa: PGH003
)


class DttotDocReportPersonal(models.Model):
    dttotdoc_report = models.ForeignKey(
        DttotDocReport,
        on_delete=models.CASCADE,
        related_name="personal_reports",
        related_query_name="personal_report",
    )
    dttotdoc_report_personal_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        max_length=36,
        unique=True,
        verbose_name=_("DTTOT Doc Report Personal ID"),
    )
    created_date = models.DateTimeField(_("Entry Created Date"), auto_now_add=True)
    last_updated_date = models.DateTimeField(_("Entry Updated Date"), auto_now=True)
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Updated by User"),
        related_name="updated_dttotDoc_personals",
        related_query_name="updated_dttotDoc_personal",
        null=True,
    )
    dsb_user_personal = models.CharField(
        _("Entry Personal User that matched with similarity > 0.8"),
        max_length=255,
        blank=True,
    )
    kode_densus_personal = models.CharField(
        _("Entry Personal User that matched with similarity > 0.8"),
        blank=True,
        max_length=20,
    )
    score_match_similarity = models.FloatField(
        _("Similarity Score"),
        default=0.0,
    )


    class Meta:
        db_table = "dttotdocreport_personal"
        verbose_name = "DTTOT Doc Report from User Personal"
        verbose_name_plural = "Multi DTTOT Doc Report from User Personal"

    def __str__(self) -> str:
        return f"{self.dttotdoc_report} - {self.dsb_user_personal} - {self.score_match_similarity} - {self.kode_densus_personal}"

