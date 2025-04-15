from __future__ import annotations

import uuid

from django.conf import settings  #type: ignore  # noqa: PGH003
from django.db import models  #type: ignore   # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore   # noqa: PGH003

from app.documents.models import Document  #type: ignore  # noqa: PGH003


class dsb_user_corporate(models.Model):  # noqa: N801
    dsb_user_corporate_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        max_length=36,
        editable=False,
        unique=True,
        verbose_name=_("User Corporate ID"),
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        related_name="dsb_user_corporates",
        related_query_name="dsb_user_corporate",
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
        related_name="updated_dsb_user_corporates",
        related_query_name="updated_dsb_user_corporate",
        null=True,
    )
    initial_registration_date = models.DateTimeField(
        _("User Registration Date before Upgrade to Corporate (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    user_name = models.CharField(  # noqa: DJ001
        _("Name of User when Initiating Registration (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    registered_user_email = models.EmailField(  # noqa: DJ001
        _("Email when Initiating Registration (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    users_phone_number = models.CharField(  # noqa: DJ001
        _("Phone Number when Initiating Registration (from Danasaham Core)"),
        max_length=20,
        blank=True,
        null=True,
    )
    users_last_modified_date = models.DateTimeField(
        _("User Entry Last Modified Date (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_pengurus_id = models.CharField(  # noqa: DJ001
        _("ID Pengurus of Corporate Investor (from Danasaham Core)"),
        max_length=36,
        blank=True,
        null=True,
    )
    pengurus_corporate_name = models.CharField(  # noqa: DJ001
        _("Name of Pengurus from Corporate (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_corporate_id_number = models.CharField(  # noqa: DJ001
        _("ID Number of Pengurus from Corporate (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    pengurus_corporate_phone_number = models.CharField(  # noqa: DJ001
        _("Pengurus Phone Number from Corporate (from Danasaham Core)"),
        max_length=20,
        blank=True,
        null=True,
    )
    pengurus_corporate_place_of_birth = models.CharField(  # noqa: DJ001
        _("Place of Birth of Pengurus (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_corporate_date_of_birth = models.DateField(
        _("Date of Birth of Pengurus (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    pengurus_corporate_npwp = models.CharField(  # noqa: DJ001
        _("NPWP of Pengurus (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    pengurus_corporate_domicile_address = models.TextField(  # noqa: DJ001
        _("Domicile Address of Pengurus (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    pengurus_corporate_jabatan = models.CharField(  # noqa: DJ001
        _("Jabatan of Pengurus (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_nominal_saham = models.CharField(  # noqa: DJ001
        _("Nominal Saham of Pengurus (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_corporate_last_update_date = models.DateTimeField(
        _("Last Update Date of Pengurus (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    users_upgrade_to_corporate_date = models.DateTimeField(
        _("Date when User Upgrade to Corporate (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_company_name = models.CharField(  # noqa: DJ001
        _("Corporate Name (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    corporate_phone_number = models.CharField(  # noqa: DJ001
        _("Corporate Phone Number (from Danasaham Core)"),
        max_length=20,
        blank=True,
        null=True,
    )
    corporate_nib = models.CharField(  # noqa: DJ001
        _("Corporate NIB (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    corporate_npwp = models.CharField(  # noqa: DJ001
        _("Corporate NPWP (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    corporate_siup = models.CharField(  # noqa: DJ001
        _("Corporate SIUP (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    corporate_skdp = models.CharField(  # noqa: DJ001
        _("Corporate SKDP (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    corporate_legal_last_modified_date = models.DateTimeField(
        _("Corporate Legal Last Modified Date (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_domicile_address = models.TextField(  # noqa: DJ001
        _("Corporate Domicile Address (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_asset = models.TextField(  # noqa: DJ001
        _("Corporate Asset (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_source_of_fund = models.TextField(  # noqa: DJ001
        _("Corporate Source of Fund (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_business_field = models.TextField(  # noqa: DJ001
        _("Corporate Business Field (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_type_of_annual_income = models.TextField(  # noqa: DJ001
        _("Corporate Type of Annual Income (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_annual_income = models.TextField(  # noqa: DJ001
        _("Corporate Annual Income (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_investment_goals = models.TextField(  # noqa: DJ001
        _("Corporate Investment Goals (from Danasaham Core)"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.dsb_user_corporate_id} - {self.corporate_company_name} - {self.corporate_business_field}"

