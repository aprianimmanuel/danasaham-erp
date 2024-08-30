from __future__ import annotations

from django.urls import path, re_path

from app.config.dttotDocReportPublisher.views import (
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
