from __future__ import annotations

from django.urls import path

from app.config.dsb_user_corporate.views import (
    DsbUserCorporateListView,
    DsbUserCorporateDetailView,
)

app_name = "dsb_user_corporate"

urlpatterns = [
    path(
        "api/dsb-user-corporate/list/",
        DsbUserCorporateListView.as_view(),
        name="dsb-user-corporate-list",
    ),
    path(
        "api/dsb-user-corporate/details/<uuid:dsb_user_corporate_id>/",
        DsbUserCorporateDetailView.as_view(),
        name="dsb-user-corporate-details",
    ),
]
