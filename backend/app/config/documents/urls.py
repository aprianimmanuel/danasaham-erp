from __future__ import annotations

from django.urls import path

from app.config.documents.views import DocumentDetailView, DocumentListView

app_name = "documents"

urlpatterns = [
    path("api/documents/list/", DocumentListView.as_view(), name="document-list"),
    path(
        "api/documents/details/<uuid:document_id>/",
        DocumentDetailView.as_view(),
        name="document-details",
    ),
]
