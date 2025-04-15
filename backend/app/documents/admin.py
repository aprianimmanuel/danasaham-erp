"""Django admin customization."""

from __future__ import annotations

from typing import ClassVar

from django.contrib import admin  #type: ignore  # noqa: PGH003

from app.documents.models import Document  #type: ignore  # noqa: PGH003


class DocumentAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "document_id",
        "document_name",
        "document_type",
        "created_by_username",
        "updated_by_username",
    ]
    search_fields: ClassVar[list[str]] = [
        "document_name",
        "document_type",
        "created_by__username",
        "updated_by__username",
    ]
    readonly_fields = ("document_id",)

    def created_by_username(self, obj: Document) -> str:
        """Display the username of the creator."""
        return obj.created_by.username

    created_by_username.short_description = "Created By"  # type: ignore  # noqa: PGH003

    def updated_by_username(self, obj: Document) -> str:
        """Display the username of the person who last updated the document."""
        return obj.updated_by.username

    updated_by_username.short_description = "Updated By"  # type: ignore  # noqa: PGH003


admin.site.register(Document, DocumentAdmin)

