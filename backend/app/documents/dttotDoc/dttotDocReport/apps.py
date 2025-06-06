from __future__ import annotations

from django.apps import AppConfig  #type: ignore # noqa: PGH003

from .signals import (
    dttot_doc_report_status_done,
    dttot_doc_report_status_failed,
    handle_status_done,
    handle_status_failed,
)


class DttotDocReportConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app.documents.dttotDoc.dttotDocReport"

    def ready(self) -> None:
        import app.documents.dttotDoc.dttotDocReport.tasks  #type: ignore # noqa: PGH003, F401

        dttot_doc_report_status_failed.connect(handle_status_failed)
        dttot_doc_report_status_done.connect(handle_status_done)
