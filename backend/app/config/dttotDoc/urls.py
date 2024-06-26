from __future__ import annotations

from django.urls import path

from app.config.dttotDoc.views import DttotDocDetailView, DttotDocListView

app_name = "dttotdocs"

urlpatterns = [
    path(
        "api/documents/dttotdocs/list/<uuid:document_id>/",
        DttotDocListView.as_view(),
        name="dttot-doc-list",
    ),
    path(
        "api/documents/dttotdocs/details/<uuid:dttot_id>/",
        DttotDocDetailView.as_view(),
        name="dttot-doc-detail",
    ),
]
