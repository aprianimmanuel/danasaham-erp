from __future__ import annotations

from django.urls import path, re_path  #type: ignore # noqa: PGH003

from app.documents.dttotDoc.dttotDocReportPersonal.views import (  #type: ignore # noqa: PGH003
    dttotDocReportPersonalDetailView,
    dttotDocReportPersonalView,
)

app_name = "dttotdocreportpersonal"

urlpatterns = [
    path(
        "api/documents/dttotdocreport/dttotdocreportpersonal/list/",
        dttotDocReportPersonalView.as_view(),
        name="dttotdocreportpersonal-list",
    ),
    re_path(
        r"^api/documents/dttotdocreport/dttotdocreportpersonal/details/$",
        dttotDocReportPersonalDetailView.as_view(),
        name="dttotdocreportpersonal-detail",
    ),
]
