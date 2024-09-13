from __future__ import annotations

import hashlib
import os
import uuid
from typing import Any

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

    def create_user(
        self, email: str, username: str, password: str | None = None, **extra_fields: Any,
    ) -> User:
        """Create and return a new user.

        Args:
        ----
            email (str): The email address of the user.
            username (str): The username of the user.
            password (Optional[str], optional): The password for the user. Defaults to None.
            **extra_fields (Any): Additional fields to be set on the user.

        Raises:
        ------
            ValueError: If no email is provided.

        Returns:
        -------
            User: The newly created user.

        """
        if not email:
            raise ValueError(_("The Email field must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(
        self, email: str, username: str, password: str | None = None, **extra_fields: Any,
    ) -> User:
        """Create and return a new superuser.

        Args:
        ----
            email (str): The email address of the user.
            username (str): The username of the user.
            password (Optional[str], optional): The password for the user. Defaults to None.
            **extra_fields (Any): Additional fields to be set on the user.

        Returns:
        -------
            User: The newly created user.

        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""

    user_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        max_length=36,
        verbose_name=_("User ID"),
        unique=True,
    )
    email = models.EmailField(_("email_address"), unique=True)
    username = models.CharField(_("username"), max_length=150, unique=True)
    is_active = models.BooleanField(_("active"), default=True)
    is_staff = models.BooleanField(_("staff status"), default=False)
    email_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # noqa: RUF012

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
    last_name = models.CharField(_("Last Name"), max_length=50, blank=True)

    def __str__(self) -> str:
        return self.user.username


def encrypt_filename(filename: str) -> str:
    """Use SHA-256 to hash the filename and preserve the original file extension.

    Args:
    ----
        filename (str): The name of the file.

    Returns:
    -------
        str: The encrypted filename.

    """
    sha256_hash = hashlib.sha256()
    sha256_hash.update(filename.encode("utf-8"))
    encrypted_filename = sha256_hash.hexdigest()
    file_extension = os.path.splitext(filename)[1]  # noqa: PTH122
    return encrypted_filename + file_extension


def save_file_to_instance(
    instance: Any, uploaded_file: Any,
) -> None:
    """Save an uploaded file to a Document instance.

    The file is saved to the instance's document_file field.

    Args:
    ----
        instance (Document): The Document instance to save the file to.
        uploaded_file (SimpleUploadedFile): The uploaded file to save.

    Returns:
    -------
        None: No return value.

    """
    if uploaded_file:
        filename = uploaded_file.name
        encrypted_filename = encrypt_filename(filename)
        file_path = document_directory_path(instance, encrypted_filename)
        file_content = uploaded_file.read()

        content_file = ContentFile(file_content, name=os.path.basename(file_path))  # noqa: PTH119
        instance.document_file.save(content_file.name, content_file, save=False)


def document_directory_path(
    instance: Any, filename: str,
) -> str:
    """Generate a path to store an uploaded file.

    The path is generated using the Document instance's fields, and the
    filename of the uploaded file.

    Args:
    ----
        instance (Any): The instance to generate a path for.
        filename (str): The filename of the uploaded file.

    Returns:
    -------
        str: The generated path.

    """
    date_now = instance.created_date or now()
    app_name = instance._meta.app_label  # noqa: SLF001

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
    description = models.TextField(blank=True)
    document_file = models.FileField(
        upload_to=document_directory_path,
        blank=True,
        null=True,
    )
    created_date = models.DateTimeField(auto_now_add=True)
    document_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        max_length=36,
        unique=True,
        verbose_name=_("Document ID"),
    )
    document_file_type = models.CharField(max_length=50, blank=True)
    document_type = models.CharField(max_length=50)
    last_update_date = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_documents",
    )
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_documents",
    )

    def __str__(self) -> str:
        return self.document_name

    def save(
        self,
        *args: Any,
        skip_file_save: bool = False,
        **kwargs: Any,
    ) -> None:
        """Save the document instance.

        Args:
        ----
            *args: Variable length argument list.
            skip_file_save: Whether to skip saving the file.
            **kwargs: Arbitrary keyword arguments.

        Returns:
        -------
            None


        """
        if self.document_file and not skip_file_save:
            save_file_to_instance(self, self.document_file)
        super().save(*args, **kwargs)

    def document_file_required(self) -> bool:
        """Check if document file is required.

        Returns
        -------
        bool: True if document file is required, False otherwise.

        """
        return self.document_type in [
            "DTTOT Report",
        ]


class dttotDoc(models.Model):  # noqa: N801
    updated_at = models.DateTimeField(
        _("DTTOT Updated at"),
        auto_now=True,
        null=True)
    last_update_by = models.ForeignKey(
        "User",
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_dttot_docs",
    )
    document = models.ForeignKey(
        "Document",
        on_delete=models.SET_NULL,
        related_name="dttotDocs",
        related_query_name="dttotDoc",
        null=True,
    )
    dttot_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        max_length=36,
        unique=True,
        verbose_name=_("DTTOT ID"),
    )
    dttot_first_name = models.CharField(  # noqa: DJ001
        _("DTTOT First Name"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_middle_name = models.CharField(  # noqa: DJ001
        _("DTTOT Middle Name"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_last_name = models.CharField(  # noqa: DJ001
        _("DTTOT Last Name"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_3 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_3 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_3 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_3 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_4 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_4 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_4 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_4 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 4"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_5 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_5 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_5 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_5 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 5"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_6 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 6"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_6 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 6"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_6 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 6"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_6 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 6"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_7 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 7"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_7 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 7"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_7 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 7"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_7 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 7"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_8 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 8"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_8 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 8"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_8 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 8"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_8 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 8"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_9 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 9"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_9 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 9"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_9 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 9"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_9 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 9"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_10 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 10"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_10 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 10"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_10 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 10"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_10 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 10"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_11 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 11"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_11 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 11"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_11 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 11"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_11 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 11"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_12 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 12"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_12 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 12"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_12 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 12"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_12 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 12"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_13 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 13"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_13 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 13"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_13 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 13"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_13 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 13"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_14 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 14"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_14 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 14"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_14 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 14"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_14 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 14"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_15 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 15"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_15 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 15"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_15 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 15"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_15 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 15"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_16 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 16"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_16 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 16"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_16 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 16"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_16 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 16"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_17 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 17"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_17 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 17"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_17 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 17"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_17 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 17"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_18 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 18"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_18 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 18"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_18 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 18"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_18 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 18"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_19 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 19"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_19 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 19"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_19 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 19"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_19 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 19"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_20 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 20"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_20 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 20"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_20 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 20"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_20 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 20"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_21 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 21"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_21 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 21"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_21 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 21"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_21 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 21"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_22 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 22"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_22 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 22"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_22 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 22"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_22 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 22"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_23 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 23"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_23 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 23"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_23 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 23"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_23 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 23"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_24 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 24"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_24 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 24"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_24 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 24"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_24 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 24"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_25 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 25"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_25 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 25"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_25 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 25"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_25 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 25"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_26 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 26"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_26 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 26"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_26 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 26"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_26 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 26"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_27 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 27"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_27 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 27"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_27 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 27"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_27 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 27"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_name_28 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Name 28"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_first_name_28 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias First Name 28"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_middle_name_28 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Middle Name 28"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_alias_last_name_28 = models.CharField(  # noqa: DJ001
        _("DTTOT Alias Last Name 28"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_type = models.CharField(  # noqa: DJ001
        _("DTTOT Type"),
        max_length=255,
        blank=True,
        null=True,

    )
    dttot_kode_densus = models.CharField(  # noqa: DJ001
        _("DTTOT Kode Densus"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_place = models.CharField(  # noqa: DJ001
        _("DTTOT Birth Place"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_date_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Birth Date 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_date_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Birth Date 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_birth_date_3 = models.CharField(  # noqa: DJ001
        _("DTTOT Birth Date 3"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_nationality_1 = models.CharField(  # noqa: DJ001
        _("DTTOT Nationality 1"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_nationality_2 = models.CharField(  # noqa: DJ001
        _("DTTOT Nationality 2"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_domicile_address = models.TextField(  # noqa: DJ001
        _("DTTOT Domicile Address"),
        blank=True,
        null=True,
    )
    dttot_description_1 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 1"),
        blank=True,
        null=True,
    )
    dttot_description_2 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 2"),
        blank=True,
        null=True,
        )
    dttot_description_3 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 3"),
        blank=True,
        null=True,
    )
    dttot_description_4 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 4"),
        blank=True,
        null=True,
    )
    dttot_description_5 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 5"),
        blank=True,
        null=True,
    )
    dttot_description_6 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 1"),
        blank=True,
        null=True,
    )
    dttot_description_7 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 2"),
        blank=True,
        null=True,
        )
    dttot_description_8 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 3"),
        blank=True,
        null=True,
    )
    dttot_description_9 = models.TextField(  # noqa: DJ001
        _("DTTOT Description 4"),
        blank=True,
        null=True,
    )
    dttot_nik_ktp = models.CharField(  # noqa: DJ001
        _("DTTOT NIK KTP"),
        max_length=255,
        blank=True,
        null=True,
    )
    dttot_passport_number = models.CharField(  # noqa: DJ001
        _("DTTOT Passport Number"),
        max_length=255,
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.dttot_first_name} {self.dttot_last_name} - {self.dttot_type}"


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


class dsb_user_publisher(models.Model):  # noqa: N801
    dsb_user_publisher_id = models.CharField(
        default=uuid.uuid4,
        primary_key=True,
        editable=False,
        max_length=36,
        unique=True,
        verbose_name=_("Danasaham User Publisher ID"),
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

    def __str__(self) -> str:
        return f"{self.dsb_user_publisher_id} - {self.publisher_registered_name} - {self.publisher_business_field}"


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


class dttotDocReport(models.Model):  # noqa: N801
    dttotdoc_report_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        max_length=36,
        unique=True,
        verbose_name=_("DTTOT Doc Report ID"),
    )
    document = models.OneToOneField(
        "Document",
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

    def __str__(self) -> str:
        return f"{self.dttotdoc_report_id} - {self.document} - {self.created_date}"


class dttotDocReportPersonal(models.Model):  # noqa: N801
    dttotdoc_report = models.ForeignKey(
        dttotDocReport,
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

    def __str__(self) -> str:
        return f"{self.dttotdoc_report} - {self.dsb_user_personal} - {self.score_match_similarity} - {self.kode_densus_personal}"


class dttotDocReportCorporate(models.Model):  # noqa: N801
    dttotdoc_report = models.ForeignKey(
        dttotDocReport,
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

    def __str__(self) -> str:
        return f"{self.dttotdoc_report} - {self.dsb_user_corporate} - {self.score_match_similarity} - {self.kode_densus_corporate}"


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

class log_tracker_publisher(models.Model):   # noqa: N801
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="log_tracker_publishers",
        related_query_name="log_tracker_publisher",
    )
    log_tracker_publisher_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        max_length=36,
        unique=True,
        verbose_name=_("Log Tracker Publisher ID"),
    )
    created_date = models.DateTimeField(_("Entry Created Date"), auto_now_add=True)
    last_updated_date = models.DateTimeField(_("Entry Updated Date"), auto_now=True)
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Updated by User"),
        related_name="updated_log_tracker_publishers",
        related_query_name="updated_log_tracker_publisher",
        null=True,
    )
    core_dsb_user_id = models.CharField(  # noqa: DJ001
        _("ID of User From Danasaham Core"),
        max_length=36,
        blank=True,
        null=True,
    )
    publisher_company_name = models.CharField(
        _("Company Name"),
        max_length=255,
        blank=True,
    )
    initial_registration_date = models.DateTimeField(
        _("Initial Registration Date"),
        blank=True,
        null=True,
    )
    publisher_upgrade_date = models.DateTimeField(
        _("Publisher Upgrade Date"),
        blank=True,
        null=True,
    )
    publisher_legal_data_input_created_date = models.DateTimeField(
        _("Publisher Legal Data Input Created Date"),
        blank=True,
        null=True,
    )
    publisher_finance_data_input_created_date = models.DateTimeField(
        _("Publisher Finance Data Input Created Date"),
        blank=True,
        null=True,
    )
    publisher_proposal_data_input_created_date = models.DateTimeField(
        _("Publisher Proposal Data Input Created Date"),
        blank=True,
        null=True,
    )
    primary_va_registration_date = models.DateTimeField(
        _("Primary VA Registration Registration Date"),
        blank=True,
        null=True,
    )
    va_operational_approval_created_date = models.DateTimeField(
        _("VA Operational Approval Created Date"),
        blank=True,
        null=True,
    )
    approval_registration_fee_date = models.DateTimeField(
        _("Approval Registration Fee Date"),
        blank=True,
        null=True,
    )
    primary_offering_input_date = models.DateTimeField(
        _("Primary Offering Input Date"),
        blank=True,
        null=True,
    )
    confirmation_primary_offering_date = models.DateTimeField(
        _("Confirmation Primary Offering Date"),
        blank=True,
        null=True,
    )
    cbestreporting_date = models.DateTimeField(
        _("CBEST Reporting Date"),
        blank=True,
        null=True,
    )
    investation_succcess_sk_upload_date = models.DateTimeField(
        _("Investation Succcess SK Upload Date"),
        blank=True,
        null=True,
    )
    investation_success_check_date = models.DateTimeField(
        _("Investation Success Check Date"),
        blank=True,
        null=True,
    )
    investation_success_approval_date = models.DateTimeField(
        _("Investation Success Approval Date"),
        blank=True,
        null=True,
    )
    investation_success_fund_transfer_date = models.DateTimeField(
        _("Investation Success Fund Transfer Date"),
        blank=True,
        null=True,
    )
    investation_success_share_distribution_date = models.DateTimeField(
        _("Investation Success Share Distribution Date"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.document} - {self.core_dsb_user_id} - {self.publisher_company_name}"

class log_tracker_personal(models.Model):   # noqa: N801
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="log_tracker_personals",
        related_query_name="log_tracker_personal",
    )
    log_tracker_personal_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        max_length=36,
        unique=True,
        verbose_name=_("Log Tracker Personal ID"),
    )
    created_date = models.DateTimeField(_("Entry Created Date"), auto_now_add=True)
    last_updated_date = models.DateTimeField(_("Entry Updated Date"), auto_now=True)
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Updated by User"),
        related_name="updated_log_tracker_personals",
        related_query_name="updated_log_tracker_personal",
        null=True,
    )
    core_dsb_user_id = models.CharField(  # noqa: DJ001
        _("ID of User From Danasaham Core"),
        max_length=36,
        blank=True,
        null=True,
    )
    personal_name = models.CharField(
        _("Personal Name"),
        max_length=255,
        blank=True,
    )
    initial_registration_date = models.DateTimeField(
        _("Initial Registration Date"),
        blank=True,
        null=True,
    )
    personal_legal_created_date = models.DateTimeField(
        _("Personal Legal Created Date"),
        blank=True,
        null=True,
    )
    personal_finance_created_date = models.DateTimeField(
        _("Personal Finance Created Date"),
        blank=True,
        null=True,
    )
    personal_ksei_id_created_date = models.DateTimeField(
        _("Personal KSEI ID Created Date"),
        blank=True,
        null=True,
    )
    personal_limit_last_modified_date = models.DateTimeField(
        _("Personal Limit Last Modified Date"),
        blank=True,
        null=True,
    )
    personal_data_checking_date = models.DateTimeField(
        _("Personal Data Checking Date"),
        blank=True,
        null=True,
    )
    initial_primary_investment_date = models.DateTimeField(
        _("Initial Primary Investment Date"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.document} - {self.core_dsb_user_id} - {self.personal_name}"

class log_tracker_corporate(models.Model):  # noqa: N801
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="log_tracker_corporates",
        related_query_name="log_tracker_corporate",
    )
    log_tracker_corporate_id = models.CharField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True,
        max_length=36,
        unique=True,
        verbose_name=_("Log Tracker Corporate ID"),
    )
    created_date = models.DateTimeField(
        _("Entry Created Date"),
        auto_now_add=True,
    )
    last_updated_date = models.DateTimeField(
        _("Entry Updated Date"),
        auto_now=True,
    )
    last_update_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        verbose_name=_("Last Updated by User"),
        related_name="updated_log_tracker_corporates",
        related_query_name="updated_log_tracker_corporate",
        null=True,
    )
    core_dsb_user_id = models.CharField(  # noqa: DJ001
        _("ID of User From Danasaham Core"),
        max_length=36,
        blank=True,
        null=True,
    )
    corporate_company_name = models.CharField(
        _("Corporate Name"),
        max_length=255,
        blank=True,
    )
    initial_registration_date = models.DateTimeField(
        _("Initial Registration Date"),
        blank=True,
        null=True,
    )
    corporate_legal_created_date = models.DateTimeField(
        _("Corporate Legal Created Date"),
        blank=True,
        null=True,
    )
    corporate_finance_created_date = models.DateTimeField(
        _("Corporate Finance Created Date"),
        blank=True,
        null=True,
    )
    corporate_ksei_id_created_date = models.DateTimeField(
        _("Corporate KSEI ID Created Date"),
        blank=True,
        null=True,
    )
    corporate_info_check_date = models.DateTimeField(
        _("Corporate Info Checking Date"),
        blank=True,
        null=True,
    )
    initial_primary_investment_date = models.DateTimeField(
        _("Initial Primary Investment Date"),
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.document} - {self.core_dsb_user_id} - {self.corporate_company_name}"
