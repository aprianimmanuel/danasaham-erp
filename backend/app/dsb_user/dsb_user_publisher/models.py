from __future__ import annotations

import uuid

from django.conf import settings  #type: ignore  # noqa: PGH003
from django.db import models  #type: ignore   # noqa: PGH003
from django.utils.translation import gettext_lazy as _  # type: ignore   # noqa: PGH003

from app.documents.models import Document  #type: ignore  # noqa: PGH003


class DsbUserPublisher(models.Model):
    dsb_user_publisher_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        max_length=36,
        unique=True,
        verbose_name=_("Danasaham User Publisher ID"),
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        related_name="dsb_user_publisher",
        related_query_name="dsb_user_publisher",
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
        related_name="updated_dsb_user_publishers",
        related_query_name="updated_dsb_user_publisher",
        null=True,
    )
    initial_registration_date = models.DateTimeField(
        _("User Initial Registration Date (from Danasaham Core)"),
        auto_now=False,
        auto_now_add=False,
        blank=True,
        null=True,
    )
    coredsb_user_id = models.CharField(  # noqa: DJ001
        _("ID of User From Danasaham Core"),
        max_length=36,
        null=True,
    )
    user_name = models.CharField(  # noqa: DJ001
        _("Name of User when Initiating Registration (from Danasaham Core)"),
        max_length=255,
        null=True,
        blank=True,
    )
    registered_user_email = models.EmailField(  # noqa: DJ001
        _("Email when Initiating Registration (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    users_phone_number = models.CharField(  # noqa: DJ001
        _("Phone Number when Initiating Registration (from Danasaham Core)"),
        max_length=20,
        null=True,
        blank=True,
    )
    users_last_modified_date = models.DateTimeField(
        _("User Entry Last Modified Date (from Danasaham Core)"),
        auto_now=False,
        auto_now_add=False,
        blank=True,
        null=True,
    )
    user_upgrade_to_publisher_date = models.DateTimeField(
        _("Date when User Upgrade to Publisher (from Danasaham Core)"),
        auto_now=False,
        auto_now_add=False,
        blank=True,
        null=True,
    )
    publisher_registered_name = models.CharField(  # noqa: DJ001
        _("Publisher Registered Name (from Danasaham Core)"),
        max_length=255,
        null=True,
        blank=True,
    )
    publisher_corporate_type = models.CharField(  # noqa: DJ001
        _("Publisher Corporate Type (from Danasaham Core)"),
        max_length=255,
        null=True,
        blank=True,
    )
    publisher_phone_number = models.CharField(  # noqa: DJ001
        _("Publisher Phone Number (from Danasaham Core)"),
        max_length=20,
        null=True,
        blank=True,
    )
    publisher_bank_account_number = models.CharField(  # noqa: DJ001
        _("Publisher Bank Account Number (from Danasaham Core)"),
        max_length=100,
        null=True,
        blank=True,
    )
    publisher_bank_account_provider_name = models.CharField(  # noqa: DJ001
        _("Publisher Bank Account Provider Name (from Danasaham Core)"),
        max_length=255,
        null=True,
        blank=True,
    )
    publisher_business_field = models.CharField(  # noqa: DJ001
        _("Publisher Business Field (from Danasaham Core)"),
        max_length=255,
        null=True,
        blank=True,
    )
    publisher_main_business = models.CharField(  # noqa: DJ001
        _("Publisher Main Business (from Danasaham Core)"),
        max_length=255,
        null=True,
        blank=True,
    )
    domicile_address_publisher_1 = models.TextField(  # noqa: DJ001
        _("Domicile Address Publisher Line 1 (from Danasaham Core)"),
        null=True,
        blank=True,
    )
    domicile_address_publisher_2 = models.TextField(  # noqa: DJ001
        _("Domicile Address Publisher Line 2 (from Danasaham Core)"),
        null=True,
        blank=True,
    )
    domicile_address_publisher_3_city = models.CharField(  # noqa: DJ001
        _("Domicile Address Publisher City (from Danasaham Core)"),
        max_length=255,
        null=True,
        blank=True,
    )
    publisher_last_modified_date = models.DateTimeField(
        _("Publisher Entry Last Modified Date (from Danasaham Core)"),
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True,
    )
    publisher_pengurus_id = models.CharField(  # noqa: DJ001
        _("Pengurus ID (from Danasaham Core)"),
        max_length=36,
        null=True,
        blank=True,
    )
    publisher_pengurus_name = models.CharField(  # noqa: DJ001
        _("Pengurus Name (from Danasaham Core)"),
        max_length=255,
        null=True,
        blank=True,
    )
    publisher_pengurus_id_number = models.CharField(  # noqa: DJ001
        _("Pengurus ID Number (from Danasaham Core)"),
        max_length=50,
        null=True,
        blank=True,
    )
    publisher_pengurus_phone_number = models.CharField(  # noqa: DJ001
        _("Pengurus Phone Number (from Danasaham Core)"),
        max_length=20,
        null=True,
        blank=True,
    )
    publisher_pengurus_role_as = models.CharField(  # noqa: DJ001
        _("Role as (from Danasaham Core)"),
        max_length=255,
        null=True,
        blank=True,
    )
    publisher_jabatan_pengurus = models.CharField(  # noqa: DJ001
        _("Jabatan Pengurus (from Danasaham Core)"),
        max_length=255,
        null=True,
        blank=True,
    )
    publisher_address_pengurus = models.TextField(  # noqa: DJ001
        _("Address Pengurus (from Danasaham Core)"),
        null=True,
        blank=True,
    )
    publisher_tgl_lahir_pengurus = models.DateField(
        _("Tanggal Lahir Pengurus (from Danasaham Core)"),
        null=True,
        blank=True,
    )
    publisher_tempat_lahir_pengurus = models.CharField(  # noqa: DJ001
        _("Tempat Lahir Pengurus (from Danasaham Core)"),
        max_length=255,
        null=True,
        blank=True,
    )
    pengurus_publisher_last_modified_date = models.DateTimeField(
        _("Pengurus Publisher Entry Last Modified Date (from Danasaham Core)"),
        auto_now=False,
        auto_now_add=False,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = "dsb_user_publisher"
        verbose_name = "DSB User Publisher"
        verbose_name_plural = "DSB User Publishers"

    def __str__(self) -> str:
        return f"{self.dsb_user_publisher_id} - {self.publisher_registered_name} - {self.publisher_business_field}"

