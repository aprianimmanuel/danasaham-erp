from __future__ import annotations

from django.urls import path, re_path  #type: ignore # noqa: PGH003

from app.dttotDocReport.views import (  #type: ignore # noqa: PGH003
    dttotDocReportDetailView,
    dttotDocReportView,
)

app_name = "dttotdocreport"

urlpatterns = [
    path(
        "api/documents/dttotdocreport/list/",
        dttotDocReportView.as_view(),
        name="dttotdocreport-list",
    ),
    re_path(
        r"api/documents/dttotdocreport/details/$",
        dttotDocReportDetailView.as_view(),
        name="dttotdocreport-detail",
    ),
]
