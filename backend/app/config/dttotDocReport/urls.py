from __future__ import annotations

from django.urls import path, re_path

from app.config.dttotDocReport.views import dttotDocReportDetailView, dttotDocReportView

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
