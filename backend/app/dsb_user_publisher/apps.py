from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003


class DsbUserPublisherConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.dsb_user_publisher"
    verbose_name = "DSB User Publisher"

    def ready(self) -> None:
        import app.dsb_user_publisher.tasks  #type: ignore # noqa: PGH003, F401
