from __future__ import annotations

from django.urls import path  #type: ignore # noqa: PGH003

from app.documents.dttotDoc.views import (  #type: ignore # noqa: PGH003
    DttotDocDetailView,
    DttotDocListView,
)

app_name = "DttotDoc"

urlpatterns = [
    path(
        "dttotdocs/list/",
        DttotDocListView.as_view(),
        name="dttot-doc-list",
    ),
    path(
        "dttotdocs/details/",
        DttotDocDetailView.as_view(),
        name="dttot-doc-detail",
    ),
]
