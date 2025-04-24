from __future__ import annotations

from django.apps import AppConfig  # type: ignore  # noqa: PGH003


class UserSignedDocumentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.user.user_signed_document"
    verbose_name = "User Signed Document"
    verbose_name_plural = "User Signed Documents"

    def ready(self) -> None:
        pass