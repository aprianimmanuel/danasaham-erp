from __future__ import annotations

from django.urls import path, re_path  #type: ignore  # noqa: PGH003

from app.documents.views import (  #type: ignore  # noqa: PGH003
    DocumentDetailView,
    DocumentListView,
)

app_name = "documents"

urlpatterns = [
    path("api/documents/list/", DocumentListView.as_view(), name="document-list"),
    re_path(
        r"^api/documents/details/$",
        DocumentDetailView.as_view(),
        name="document-details",
    ),
]
