from __future__ import annotations

from django.urls import path, re_path  #type: ignore # noqa: PGH003

from app.dttotDocReportCorporate.views import (  #type: ignore # noqa: PGH003
    dttotDocReportCorporateDetailView,
    dttotDocReportCorporateView,
)

app_name = "dttotdocreportcorporate"

urlpatterns = [
    path(
        "api/documents/dttotdocreport/dttotdocreportcorporate/list/",
        dttotDocReportCorporateView.as_view(),
        name="dttotdocreportcorporate-list",
    ),
    re_path(
        r"^api/documents/dttotdocreport/dttotdocreportcorporate/details/$",
        dttotDocReportCorporateDetailView.as_view(),
        name="dttotdocreportcorporate-detail",
    ),
]
