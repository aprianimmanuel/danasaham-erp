from __future__ import annotations

import uuid

from django.conf import settings  #type: ignore  # noqa: PGH003
from django.db import models  #type: ignore   # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore   # noqa: PGH003

from app.dttotDocReport.models import dttotDocReport  #type: ignore  # noqa: PGH003


class dttotDocReportPublisher(models.Model):  # noqa: N801
    dttotdoc_report = models.ForeignKey(
        dttotDocReport,
        on_delete=models.CASCADE,
        related_name="publisher_reports",
        related_query_name="publisher_report",
    )
    dttotdoc_report_publisher_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        max_length=36,
        unique=True,
        verbose_name=_("DTTOT Doc Report Publisher ID"),
    )
    created_date = models.DateTimeField(_("Entry Created Date"), auto_now_add=True)
    last_updated_date = models.DateTimeField(_("Entry Updated Date"), auto_now=True)
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Updated by User"),
        related_name="updated_dttotDoc_publishers",
        related_query_name="updated_dttotDoc_publisher",
        null=True,
    )
    dsb_user_publisher = models.CharField(
        _("User Publisher ID"),
        max_length=255,
        blank=True,
    )
    kode_densus_publisher = models.CharField(
        _("Entry Personal User that matched with similarity > 0.8"),
        blank=True,
        max_length=20,
    )
    score_match_similarity = models.FloatField(
        _("Similarity Score"),
        default=0.0,
    )

    def __str__(self) -> str:
        return f"{self.dttotdoc_report} - {self.dsb_user_publisher} - {self.score_match_similarity} - {self.kode_densus_publisher}"
