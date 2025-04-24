from __future__ import annotations

from django.urls import path, re_path  #type: ignore # noqa: PGH003

from app.documents.dttotDoc.dttotDocReportPublisher.views import (  #type: ignore # noqa: PGH003
    dttotDocReportPublisherDetailView,
    dttotDocReportPublisherView,
)

app_name = "dttotdocreportpublisher"

urlpatterns = [
    path(
        "api/documents/dttotdocreport/dttotdocreportpublisher/list/",
        dttotDocReportPublisherView.as_view(),
        name="dttotdocreportpublisher-list",
    ),
    re_path(
        r"^api/documents/dttotdocreport/dttotdocreportpublisher/details/$",
        dttotDocReportPublisherDetailView.as_view(),
        name="dttotdocreportpublisher-detail",
    ),
]
