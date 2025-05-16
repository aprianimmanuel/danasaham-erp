from __future__ import annotations

from django.urls import path, re_path  #type: ignore # noqa: PGH003

from app.documents.dttotDoc.dttotDocReport.views import (  #type: ignore # noqa: PGH003
    dttotDocReportDetailView,
    dttotDocReportView,
)

app_name = "dttotdocreport"

urlpatterns = [
    path(
        "dttotdocreport/list/",
        dttotDocReportView.as_view(),
        name="dttotdocreport-list",
    ),
    re_path(
        r"dttotdocreport/details/$",
        dttotDocReportDetailView.as_view(),
        name="dttotdocreport-detail",
    ),
]
