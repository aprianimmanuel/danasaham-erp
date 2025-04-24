"""Django admin customization."""

from __future__ import annotations

from typing import ClassVar

import pytz  #type: ignore  # noqa: PGH003
from django.contrib import admin  #type: ignore  # noqa: PGH003
from django.utils import timezone  #type: ignore  # noqa: PGH003
from django.utils.html import format_html  #type: ignore  # noqa: PGH003

from app.documents.dttotDoc.models import DttotDoc  #type: ignore  # noqa: PGH003


class DttotDocAdmin(admin.ModelAdmin):
    list_display: ClassVar[list[str]] = [
        "document_id",
        "dttot_id",
        "dttot_type",
        "display_username",
        "formatted_updated_at",
    ]
    search_fields: ClassVar[list[str]] = [
        "dttot_id",
        "dttot_type",
        "dttot_first_name",
        "dttot_last_name",
        "user__username",
    ]
    list_filter: ClassVar[list[str]] = ["dttot_type", "updated_at"]
    readonly_fields = ("document_id", "dttot_id")

    def display_username(self, obj: DttotDoc) -> str:
        """Display the username associated with the document."""
        return obj.user.username

    display_username.short_description = "Username" # type: ignore   # noqa: PGH003

    def formatted_updated_at(self, obj: DttotDoc) -> str:
        """Display updated_at time in GMT+7 timezone."""
        local_tz = pytz.timezone("Asia/Jakarta")
        local_time = timezone.localtime(obj.updated_at, local_tz)
        return format_html("<span>{}</span>", local_time.strftime("%Y-%m-%d %H:%M:%S"))

    formatted_updated_at.short_description = "Updated At (GMT+7)" # type: ignore  # noqa: PGH003

admin.site.register(DttotDoc, DttotDocAdmin)
