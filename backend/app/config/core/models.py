from __future__ import annotations

import hashlib
import os
import uuid

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.files.base import ContentFile
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager for user profiles."""

    def create_user(self, email, username, password=None, **extra_fields):
        """Create and return a new user."""
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and return a new superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    user_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    email = models.EmailField(_("email_address"), unique=True)
    username = models.CharField(_("username"), max_length=150, unique=True, null=True)
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        return self.email


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(max_length=500, blank=True)
    phone_number = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    first_name = models.CharField(_("First Name"), max_length=50, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=50, blank=True, null=True)

    def __str__(self) -> str:
        return self.user.username


def encrypt_filename(filename):
    """Use SHA-256 to hash the filename and preserve the original file extension."""
    sha256_hash = hashlib.sha256()
    sha256_hash.update(filename.encode("utf-8"))
    encrypted_filename = sha256_hash.hexdigest()
    file_extension = os.path.splitext(filename)[1]
    return encrypted_filename + file_extension


def save_file_to_instance(instance, uploaded_file) -> None:
    if uploaded_file:
        filename = uploaded_file.name
        encrypted_filename = encrypt_filename(filename)
        file_path = document_directory_path(instance, encrypted_filename)
        file_content = uploaded_file.read()

        content_file = ContentFile(file_content, name=os.path.basename(file_path))
        instance.document_file.save(content_file.name, content_file, save=False)


def document_directory_path(instance, filename):
    date_now = instance.created_date or now()
    app_name = instance._meta.app_label

    return "{app_name}/{document_type}/{year}/{month}/{day}/{created_by}/{filename}".format(
        document_type=instance.document_type,
        app_name=app_name,
        year=date_now.year,
        month=date_now.strftime("%m"),
        day=date_now.strftime("%d"),
        created_by=instance.created_by.user_id if instance.created_by else "unknown",
        filename=filename,
    )


class Document(models.Model):
    document_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    document_file = models.FileField(
        upload_to=document_directory_path,
        blank=True,
        null=True,
    )
    created_date = models.DateTimeField(auto_now_add=True)
    document_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    document_file_type = models.CharField(max_length=50, null=True, blank=True)
    document_type = models.CharField(max_length=50)
    updated_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_documents",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_documents",
    )

    def save(self, *args, **kwargs) -> None:
        if (
            self.document_file
            and not self._state.adding
            and not kwargs.get("skip_file_save", False)
        ):
            save_file_to_instance(self, self.document_file)
        super().save(*args, **kwargs)

    def document_file_required(self):
        return self.document_type in [
            "PDF",
            "DTTOT Document",
            "DSB User Personal List Document",
        ]

    def __str__(self) -> str:
        return self.document_name


class dttotDoc(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Created by User"),
        null=True,
    )
    updated_at = models.DateTimeField(_("DTTOT Updated at"), auto_now=True)
    document = models.ForeignKey(
        "Document",
        on_delete=models.SET_NULL,
        related_name="dttotDocs",
        related_query_name="dttotDoc",
        null=True,
    )
    dttot_id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    dttot_first_name = models.CharField(
        _("DTTOT First Name"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_middle_name = models.CharField(
        _("DTTOT Middle Name"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_last_name = models.CharField(
        _("DTTOT Last Name"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_1 = models.CharField(
        _("DTTOT Alias Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_1 = models.CharField(
        _("DTTOT Alias First Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_1 = models.CharField(
        _("DTTOT Alias Middle Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_1 = models.CharField(
        _("DTTOT Alias Last Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_2 = models.CharField(
        _("DTTOT Alias Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_2 = models.CharField(
        _("DTTOT Alias First Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_2 = models.CharField(
        _("DTTOT Alias Middle Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_2 = models.CharField(
        _("DTTOT Alias Last Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_3 = models.CharField(
        _("DTTOT Alias Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_3 = models.CharField(
        _("DTTOT Alias First Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_3 = models.CharField(
        _("DTTOT Alias Middle Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_3 = models.CharField(
        _("DTTOT Alias Last Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_4 = models.CharField(
        _("DTTOT Alias Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_4 = models.CharField(
        _("DTTOT Alias First Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_4 = models.CharField(
        _("DTTOT Alias Middle Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_4 = models.CharField(
        _("DTTOT Alias Last Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_5 = models.CharField(
        _("DTTOT Alias Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_5 = models.CharField(
        _("DTTOT Alias First Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_5 = models.CharField(
        _("DTTOT Alias Middle Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_5 = models.CharField(
        _("DTTOT Alias Last Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_type = models.CharField(
        _("DTTOT Type"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_kode_densus = models.CharField(
        _("DTTOT Kode Densus"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_place = models.CharField(
        _("DTTOT Birth Place"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_date_1 = models.CharField(
        _("DTTOT Birth Date 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_date_2 = models.CharField(
        _("DTTOT Birth Date 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_date_3 = models.CharField(
        _("DTTOT Birth Date 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_nationality_1 = models.CharField(
        _("DTTOT Nationality 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_nationality_2 = models.CharField(
        _("DTTOT Nationality 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_domicile_address = models.TextField(
        _("DTTOT Domicile Address"),
        blank=True,
        null=True,
    )
    dttot_description_1 = models.TextField(
        _("DTTOT Description 1"),
        blank=True,
        null=True,
    )
    dttot_description_2 = models.TextField(
        _("DTTOT Description 2"),
        blank=True,
        null=True,
    )
    dttot_description_3 = models.TextField(
        _("DTTOT Description 3"),
        blank=True,
        null=True,
    )
    dttot_description_4 = models.TextField(
        _("DTTOT Description 4"),
        blank=True,
        null=True,
    )
    dttot_description_5 = models.TextField(
        _("DTTOT Description 5"),
        blank=True,
        null=True,
    )
    dttot_nik_ktp = models.CharField(
        _("DTTOT NIK KTP"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_passport_number = models.CharField(
        _("DTTOT Passport Number"),
        max_length=255,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.dttot_first_name} {self.dttot_last_name} - {self.dttot_type}"


class dsb_user_personal(models.Model):
    dsb_user_personal_id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Instructed by User"),
        null=True,
    )
    document = models.ForeignKey(
        "Document",
        on_delete=models.SET_NULL,
        related_name="dsb_user_personal",
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
        related_name="updated_dsb_user_personals",
        related_query_name="updated_dsb_user_personal",
        null=True,
    )
    initial_registration_date = models.DateTimeField(
        _("User Initial Registration Date (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    coredsb_user_id = models.CharField(
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
    user_name = models.CharField(
        _("Name that being registered on initial (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    users_email_registered = models.EmailField(
        _("Email being Registered Initially (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    users_last_modified_date = models.DateTimeField(
        _("User Entry Last Modified Date (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    personal_name = models.CharField(
        _("Name of User from Danasaham Core"),
        max_length=255,
        blank=True,
        null=True,
    )
    personal_phone_number = models.CharField(
        _("Mobile Number of Personal from Danasaham Core"),
        max_length=20,
        blank=True,
        null=True,
    )
    personal_nik = models.CharField(
        _("NIK of Personal (from Danasaham Core)"),
        max_length=36,
        blank=True,
        null=True,
    )
    personal_spouse = models.CharField(
        _("Personal Spouse (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    personal_mother_name = models.CharField(
        _("Personal Mother Name (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    personal_domicile_address = models.TextField(
        _("Personal Domicile Address (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    personal_domicile_address_postalcode = models.CharField(
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
    personal_investment_goals = models.CharField(
        _("Personal Investment Goals (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    personal_marital_status = models.CharField(
        _("Personal Marital Status (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    personal_birth_place = models.CharField(
        _("Personal Birth Place (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    personal_nationality = models.CharField(
        _("Personal Nationality (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    personal_source_of_fund = models.CharField(
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


class dsb_user_publisher(models.Model):
    dsb_user_publisher_id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Instructed by User"),
        null=True,
    )
    document = models.ForeignKey(
        "Document",
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
    user_name = models.CharField(
        _("Name of User when Initiating Registration (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    registered_user_email = models.EmailField(
        _("Email when Initiating Registration (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    users_phone_number = models.CharField(
        _("Phone Number when Initiating Registration (from Danasaham Core)"),
        max_length=20,
        blank=True,
        null=True,
    )
    has_email_confirmed = models.BooleanField(
        _("Has Email Confirmed (from Danasaham Core)"),
        default=False,
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
    publisher_registered_name = models.CharField(
        _("Publisher Registered Name (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    publisher_corporate_type = models.CharField(
        _("Publisher Corporate Type (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    publisher_phone_number = models.CharField(
        _("Publisher Phone Number (from Danasaham Core)"),
        max_length=20,
        blank=True,
        null=True,
    )
    publisher_business_field = models.CharField(
        _("Publisher Business Field (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    publisher_main_business = models.CharField(
        _("Publisher Main Business (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    domicile_address_publisher_1 = models.TextField(
        _("Domicile Address Publisher Line 1 (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    domicile_address_publisher_2 = models.TextField(
        _("Domicile Address Publisher Line 2 (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    domicile_address_publisher_3_city = models.CharField(
        _("Domicile Address Publisher City (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    publisher_last_modified_date = models.DateTimeField(
        _("Publisher Entry Last Modified Date (from Danasaham Core)"),
        auto_now=False,
        auto_now_add=False,
        blank=True,
        null=True,
    )
    pengurus_id = models.CharField(
        _("Pengurus ID (from Danasaham Core)"),
        max_length=36,
        blank=True,
        null=True,
    )
    pengurus_name = models.CharField(
        _("Pengurus Name (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_id_number = models.CharField(
        _("Pengurus ID Number (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    pengurus_phone_number = models.CharField(
        _("Pengurus Phone Number (from Danasaham Core)"),
        max_length=20,
        blank=True,
        null=True,
    )
    role_as = models.CharField(
        _("Role as (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    jabatan_pengurus = models.CharField(
        _("Jabatan Pengurus (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    address_pengurus = models.TextField(
        _("Address Pengurus (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    tgl_lahir_pengurus = models.DateField(
        _("Tanggal Lahir Pengurus (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    tempat_lahir_pengurus = models.CharField(
        _("Tempat Lahir Pengurus (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_publisher_last_modified_date = models.DateTimeField(
        _("Pengurus Publisher Entry Last Modified Date (from Danasaham Core)"),
        auto_now=False,
        auto_now_add=False,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.dsb_user_publisher_id} - {self.publisher_registered_name} - {self.publisher_business_field}"


class dsb_user_corporate(models.Model):
    dsb_user_corporate_id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Instructed by User"),
        null=True,
    )
    document = models.ForeignKey(
        "Document",
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
    user_name = models.CharField(
        _("Name of User when Initiating Registration (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    registered_user_email = models.EmailField(
        _("Email when Initiating Registration (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    users_phone_number = models.CharField(
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
    corporate_pengurus_id = models.CharField(
        _("ID Pengurus of Corporate Investor (from Danasaham Core)"),
        max_length=36,
        blank=True,
        null=True,
    )
    pengurus_corporate_name = models.CharField(
        _("Name of Pengurus from Corporate (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_corporate_id_number = models.CharField(
        _("ID Number of Pengurus from Corporate (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    pengurus_corporate_phone_number = models.CharField(
        _("Pengurus Phone Number from Corporate (from Danasaham Core)"),
        max_length=20,
        blank=True,
        null=True,
    )
    pengurus_corporate_place_of_birth = models.CharField(
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
    pengurus_corporate_npwp = models.CharField(
        _("NPWP of Pengurus (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    pengurus_corporate_domicile_address = models.TextField(
        _("Domicile Address of Pengurus (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    pengurus_corporate_jabatan = models.CharField(
        _("Jabatan of Pengurus (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_nominal_saham = models.CharField(
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
    users_upgrade_to_corporate = models.DateTimeField(
        _("Date when User Upgrade to Corporate (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_company_name = models.CharField(
        _("Corporate Name (from Danasaham Core)"),
        max_length=255,
        blank=True,
        null=True,
    )
    corporate_phone_number = models.CharField(
        _("Corporate Phone Number (from Danasaham Core)"),
        max_length=20,
        blank=True,
        null=True,
    )
    corporate_nib = models.CharField(
        _("Corporate NIB (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    corporate_npwp = models.CharField(
        _("Corporate NPWP (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    corporate_siup = models.CharField(
        _("Corporate SIUP (from Danasaham Core)"),
        max_length=50,
        blank=True,
        null=True,
    )
    corporate_skdp = models.CharField(
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
    corporate_domicile_address = models.TextField(
        _("Corporate Domicile Address (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_asset = models.TextField(
        _("Corporate Asset (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_source_of_fund = models.TextField(
        _("Corporate Source of Fund (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_business_field = models.TextField(
        _("Corporate Business Field (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_type_of_annual_income = models.TextField(
        _("Corporate Type of Annual Income (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_annual_income = models.TextField(
        _("Corporate Annual Income (from Danasaham Core)"),
        blank=True,
        null=True,
    )
    corporate_investment_goals = models.TextField(
        _("Corporate Investment Goals (from Danasaham Core)"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.dsb_user_corporate_id} - {self.corporate_company_name} - {self.corporate_business_field}"


class dttotDocReport(models.Model):
    dttotdoc_report_id = models.UUIDField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Instructed by User"),
        null=True,
    )
    document = models.ForeignKey(
        "Document",
        on_delete=models.SET_NULL,
        related_name="dttotDocReports",
        related_query_name="dttotDocReport",
        null=True,
    )
    dttot_id = models.ForeignKey(
        "dttotDoc",
        on_delete=models.CASCADE,
        related_name="dttotDocReports",
        related_query_name="dttotDocReport",
        null=True,
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

    def __str__(self) -> str:
        return f"{self.dttotdoc_report_id} - {self.document} - {self.created_date}"


class dttotDocReportPersonal(models.Model):
    dttotdoc_report = models.ForeignKey(
        "dttotDocReport",
        on_delete=models.SET_NULL,
        related_name="dttotDocReport_personals",
        related_query_name="dttotDocReport_personal",
        null=True,
    )
    dttotdoc_report_personal_id = models.UUIDField(
        _("DTTOT Document Report Personal ID"),
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
    )
    created_date = models.DateTimeField(_("Entry Created Date"), auto_now_add=True)
    last_updated_date = models.DateTimeField(_("Entry Updated Date"), auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Updated by User"),
        related_name="updated_dttotDoc_personals",
        related_query_name="updated_dttotDoc_personal",
        null=True,
    )
    dsb_user_personal = models.ForeignKey(
        "dsb_user_personal",
        on_delete=models.CASCADE,
        verbose_name=_("User Personal Entry from Danasaham Core"),
        related_name="matched_dsb_user_personals",
        related_query_name="matched_dsb_user_personal",
    )
    score_match_similarity = models.FloatField(
        _("Similarity Score"),
        blank=True,
        null=True,
    )
    dttot = models.ForeignKey(
        "dttotDoc",
        on_delete=models.CASCADE,
        verbose_name=_("Entry DTTOT Doc with match score similarity"),
        related_name="matched_dttotDocs",
        related_query_name="matched_dttotDoc",
    )
    kode_densus_personal = models.FloatField(
        _("Entry Personal User that matched with similarity > 0.8"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.dttotdoc_report} - {self.dsb_user_personal} - {self.score_match_similarity} - {self.kode_densus_personal}"


class dttotDocReportCorporate(models.Model):
    dttotdoc_report = models.ForeignKey(
        "dttotDocReport",
        on_delete=models.SET_NULL,
        related_name="dttotDocReport_corporates",
        related_query_name="dttotDocReport_corporate",
        null=True,
    )
    dttotdoc_report_corporate_id = models.UUIDField(
        _("DTTOT Document Report Corporate ID"),
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
    )
    created_date = models.DateTimeField(_("Entry Created Date"), auto_now_add=True)
    last_updated_date = models.DateTimeField(_("Entry Updated Date"), auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Updated by User"),
        related_name="updated_dttotDoc_corporates",
        related_query_name="updated_dttotDoc_corporate",
        null=True,
    )
    dsb_user_corporate = models.ForeignKey(
        "dsb_user_corporate",
        on_delete=models.CASCADE,
        verbose_name=_("User Corporate Entry from Danasaham Core"),
        related_name="matched_dsb_user_corporates",
        related_query_name="matched_dsb_user_corporate",
    )
    score_match_similarity = models.FloatField(
        _("Similarity Score"),
        blank=True,
        null=True,
    )
    dttot = models.ForeignKey(
        "dttotDoc",
        on_delete=models.CASCADE,
        verbose_name=_("Entry DTTOT Doc with match score similarity"),
        related_name="matched_dttotDocs_corporate",
        related_query_name="matched_dttotDoc_corporate",
    )
    kode_densus_corporate = models.FloatField(
        _("Entry Corporate User that matched with similarity > 0.8"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.dttotdoc_report} - {self.dsb_user_corporate} - {self.score_match_similarity} - {self.kode_densus_corporate}"


class dttotDocReportCorporatePengurus(models.Model):
    dttotdoc_report = models.ForeignKey(
        "dttotDocReport",
        on_delete=models.CASCADE,
        related_name="dttotDocReportCorporate_pengurus",
        related_query_name="dttotDocReportCorporate_penguru",
    )
    dttotdoc_report_pengurus_corporate_id = models.UUIDField(
        _("DTTOT Document Report Pengurus Corporate ID"),
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
    )
    pengurus_id = models.UUIDField(_("Pengurus ID"), default=uuid.uuid4, editable=False)
    pengurus_name = models.CharField(
        _("Pengurus Name"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_id_number = models.CharField(
        _("Pengurus ID Number"),
        max_length=50,
        blank=True,
        null=True,
    )
    pengurus_phone_number = models.CharField(
        _("Pengurus Phone Number"),
        max_length=20,
        blank=True,
        null=True,
    )
    pengurus_place_of_birth = models.CharField(
        _("Place of Birth of Pengurus"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_date_of_birth = models.DateField(
        _("Date of Birth of Pengurus"),
        blank=True,
        null=True,
    )
    pengurus_npwp = models.CharField(
        _("NPWP of Pengurus"),
        max_length=50,
        blank=True,
        null=True,
    )
    pengurus_domicile_address = models.TextField(
        _("Domicile Address of Pengurus"),
        blank=True,
        null=True,
    )
    pengurus_jabatan = models.CharField(
        _("Jabatan of Pengurus"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_nominal_saham = models.CharField(
        _("Nominal Saham of Pengurus"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_last_update_date = models.DateTimeField(
        _("Last Update Date of Pengurus"),
        blank=True,
        null=True,
    )
    score_match_similarity = models.FloatField(
        _("Similarity Score"),
        blank=True,
        null=True,
    )
    dttot = models.ForeignKey(
        "dttotDoc",
        on_delete=models.CASCADE,
        verbose_name=_("Entry DTTOT Doc with match score similarity"),
        related_name="matched_dttotDocs_pengurus",
        related_query_name="matched_dttotDoc_pengurus",
    )
    kode_densus_pengurus_corporate = models.FloatField(
        _("Entry Pengurus of Corporate User that matched with similarity > 0.8"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.pengurus_id} - {self.pengurus_name} - {self.pengurus_jabatan} - {self.score_match_similarity} - {self.kode_densus_pengurus_corporate}"


class dttotDocReportPublisher(models.Model):
    dttotdoc_report = models.ForeignKey(
        "dttotDocReport",
        on_delete=models.SET_NULL,
        related_name="dttotDocReport_publishers",
        related_query_name="dttotDocReport_publisher",
        null=True,
    )
    dttotdoc_report_publisher_id = models.UUIDField(
        _("DTTOT Document Publisher Report ID"),
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
    )
    created_date = models.DateTimeField(_("Entry Created Date"), auto_now_add=True)
    last_updated_date = models.DateTimeField(_("Entry Updated Date"), auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Updated by User"),
        related_name="updated_dttotDoc_publishers",
        related_query_name="updated_dttotDoc_publisher",
        null=True,
    )
    dsb_user_publisher = models.ForeignKey(
        "dsb_user_publisher",
        on_delete=models.CASCADE,
        verbose_name=_("User Publisher Entry from Danasaham Core"),
        related_name="matched_dsb_user_publishers",
        related_query_name="matched_dsb_user_publisher",
    )
    score_match_similarity = models.FloatField(
        _("Similarity Score"),
        blank=True,
        null=True,
    )
    dttot = models.ForeignKey(
        "dttotDoc",
        on_delete=models.CASCADE,
        verbose_name=_("Entry DTTOT Doc with match score similarity"),
        related_name="matched_dttotDocs_publishers",
        related_query_name="matched_dttotDoc_publisher",
    )
    kode_densus_publisher = models.FloatField(
        _("Entry Personal User that matched with similarity > 0.8"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.dttotdoc_report} - {self.dsb_user_publisher} - {self.score_match_similarity} - {self.kode_densus_publisher}"


class dttotDocReportPublisherPengurus(models.Model):
    dttotdoc_report_publisher = models.ForeignKey(
        "dttotDocReportPublisher",
        on_delete=models.CASCADE,
        related_name="dttotDocReportPublisher_pengurus",
        related_query_name="dttotDocReportPublisher_penguru",
    )
    dttotdoc_report_pengurus_publisher_id = models.UUIDField(
        _("DTTOT Document Pengurus Publisher ID"),
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
    )
    pengurus_id = models.UUIDField(_("Pengurus ID"), default=uuid.uuid4, editable=False)
    pengurus_name = models.CharField(
        _("Pengurus Name"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_id_number = models.CharField(
        _("Pengurus ID Number"),
        max_length=50,
        blank=True,
        null=True,
    )
    pengurus_phone_number = models.CharField(
        _("Pengurus Phone Number"),
        max_length=20,
        blank=True,
        null=True,
    )
    pengurus_place_of_birth = models.CharField(
        _("Place of Birth of Pengurus"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_date_of_birth = models.DateField(
        _("Date of Birth of Pengurus"),
        blank=True,
        null=True,
    )
    pengurus_npwp = models.CharField(
        _("NPWP of Pengurus"),
        max_length=50,
        blank=True,
        null=True,
    )
    pengurus_domicile_address = models.TextField(
        _("Domicile Address of Pengurus"),
        blank=True,
        null=True,
    )
    pengurus_jabatan = models.CharField(
        _("Jabatan of Pengurus"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_nominal_saham = models.CharField(
        _("Nominal Saham of Pengurus"),
        max_length=255,
        blank=True,
        null=True,
    )
    pengurus_last_update_date = models.DateTimeField(
        _("Last Update Date of Pengurus"),
        blank=True,
        null=True,
    )
    score_match_similarity = models.FloatField(
        _("Similarity Score"),
        blank=True,
        null=True,
    )
    dttot = models.ForeignKey(
        "dttotDoc",
        on_delete=models.CASCADE,
        verbose_name=_("Entry DTTOT Doc with match score similarity"),
        related_name="matched_dttotDocs_pengurus_publishers",
        related_query_name="matched_dttotDoc_pengurus_publisher",
    )
    kode_densus_pengurus_publisher = models.FloatField(
        _("Entry Personal User that matched with similarity > 0.8"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.pengurus_id} - {self.pengurus_name} - {self.pengurus_jabatan} - {self.score_match_similarity} - {self.kode_densus_pengurus_publisher}"
