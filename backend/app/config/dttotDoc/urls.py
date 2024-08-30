from __future__ import annotations

from django.urls import path, re_path

from app.config.dttotDoc.views import DttotDocDetailView, DttotDocListView

app_name = "dttotdocs"

urlpatterns = [
    path(
        "api/documents/dttotdocs/list/<uuid:identifier>/",
        DttotDocListView.as_view(),
        name="dttot-doc-list",
    ),
    path(
        r"^api/documents/dttotdocs/details/$",
        DttotDocDetailView.as_view(),
        name="dttot-doc-detail",
    ),
]
