from __future__ import annotations

from django.urls import path, re_path

from app.config.dsb_user_corporate.views import (
    DsbUserCorporateDetailView,
    DsbUserCorporateListView,
)

app_name = "dsb_user_corporate"

urlpatterns = [
    path(
        "api/dsb-user-corporate/list/",
        DsbUserCorporateListView.as_view(),
        name="dsb-user-corporate-list",
    ),
    re_path(
        r"^api/dsb-user-corporate/details/$",
        DsbUserCorporateDetailView.as_view(),
        name="dsb-user-corporate-details",
    ),
]
