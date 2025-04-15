from __future__ import annotations

import uuid

from django.conf import settings  #type: ignore  # noqa: PGH003
from django.db import models  #type: ignore   # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore   # noqa: PGH003

from app.documents.models import Document  #type: ignore  # noqa: PGH003


class dsb_user_personal(models.Model):  # noqa: N801
    dsb_user_personal_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        max_length=36,
        verbose_name=_("User Personal ID"),
        unique=True,
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        related_name="dsb_user_personals",
        related_query_name="dsb_user_personal",
        null=True,
    )
    created_date = models.DateTimeField(
        _("Data Retrieve Instruction Created Date"),
        auto_now_add=True,
    )
    updated_date = models.DateTimeField(_("Entry Update Date"), auto_now=True)
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Updated by User"),
        related_name="user_updated_dsb_user_personals",
        related_query_name="user_updated_dsb_user_personal",
        null=True,
    )
    initial_registration_date = models.DateTimeField(
        _("User Initial Registration Date (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    coredsb_user_id = models.CharField(  # noqa: DJ001
        _("ID of User From Danasaham Core"),
        max_length=36,
        blank=True,
        null=True,
    )
    user_upgrade_to_personal_date = models.DateTimeField(
        _("Date when User Upgrade to Personal (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    user_name = models.CharField(  # noqa: DJ001
        _("Name that being registered on initial (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    users_email_registered = models.EmailField(  # noqa: DJ001
        _("Email being Registered Initially (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    users_last_modified_date = models.DateTimeField(
        _("User Entry Last Modified Date (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    personal_name = models.CharField(  # noqa: DJ001
        _("Name of User from Danasaham Core"),
        max_length=255,
        blank=True,
        null=True,
    )
    personal_phone_number = models.CharField(  # noqa: DJ001
        _("Mobile Number of Personal from Danasaham Core"),
        max_length=20,
        blank=True,
        null=True,
    )
    personal_nik = models.CharField(  # noqa: DJ001
        _("NIK of Personal (from Danasaham Core)"),
        max_length=36,
        blank=True,
        null=True,
    )
    personal_gender = models.CharField(  # noqa: DJ001
        _("Gender of Personal (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    personal_spouse_name = models.CharField(  # noqa: DJ001
        _("Personal Spouse (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    personal_mother_name = models.CharField(  # noqa: DJ001
        _("Personal Mother Name (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    personal_domicile_address = models.TextField(  # noqa: DJ001
        _("Personal Domicile Address (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    personal_domicile_address_postalcode = models.CharField(  # noqa: DJ001
        _("Personal Postal Code of Domicile Address (from Danasaham Core)"),
        max_length=10,
        blank=True,
        null=True,
    )
    personal_birth_date = models.DateField(
        _("Personal Birth Date (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    personal_investment_goals = models.CharField(  # noqa: DJ001
        _("Personal Investment Goals (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    personal_marital_status = models.CharField(  # noqa: DJ001
        _("Personal Marital Status (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    personal_birth_place = models.CharField(  # noqa: DJ001
        _("Personal Birth Place (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    personal_nationality = models.CharField(  # noqa: DJ001
        _("Personal Nationality (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    personal_source_of_fund = models.CharField(  # noqa: DJ001
        _("Personal Source of Fund (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    personal_legal_last_modified_date = models.DateTimeField(
        _("Personal Legal Entry Last Modified Date (from Danasaham Core)"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.dsb_user_personal_id} - {self.personal_name} - {self.personal_phone_number}"

