from __future__ import annotations

import hashlib
import os
import uuid
from typing import Any

from django.conf import settings  #type: ignore  # noqa: PGH003
from django.core.files.base import ContentFile  #type: ignore  # noqa: PGH003
from django.db import models  #type: ignore  # noqa: PGH003
from django.utils.timezone import now  #type: ignore  # noqa: PGH003
from django.utils.translation import gettext_lazy as _  #type: ignore  # noqa: PGH003


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
    letter_number = models.CharField(max_length=200, blank=True, required=False)
    dttot_letter_number_reference = models.CharField(max_length=200, blank=True, required=False)
    police_letter_date = models.CharField(max_length=200, blank=True, required=False)
    police_letter_about = models.CharField(max_length=200, blank=True, required=False)
    police_letter_number = models.CharField(max_length=200, blank=True, required=False)

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")

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

    def letter_number_required(self) -> bool:
        """Check if letter number is required.

        Returns
        -------
        bool: True if letter number is required, False otherwise.

        """
        return self.document_type in [
            "DTTOT Report",
        ]

    def dttot_letter_number_reference_required(self) -> bool:
        """Check if DTTOT letter number reference is required.

        Returns
        -------
        bool: True if DTTOT letter number reference is required, False otherwise.

        """
        return self.document_type in [
            "DTTOT Report",
        ]

    def police_letter_date_required(self) -> bool:
        """Check if police letter date is required.

        Returns
        -------
        bool: True if police letter date is required, False otherwise.

        """
        return self.document_type in [
            "DTTOT Report",
        ]

    def police_letter_about_required(self) -> bool:
        """Check if police letter about is required.

        Returns
        -------
        bool: True if police letter about is required, False otherwise.

        """
        return self.document_type in [
            "DTTOT Report",
        ]

    def police_letter_number_required(self) -> bool:
        """Check if police letter number is required.

        Returns
        -------
        bool: True if police letter number is required, False otherwise.

        """
        return self.document_type in [
            "DTTOT Report",
        ]
