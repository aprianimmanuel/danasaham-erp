from __future__ import annotations

from django.urls import path, re_path  #type: ignore # noqa: PGH003

from app.dsb_user.dsb_user_corporate.views import (  #type: ignore # noqa: PGH003
    DsbUserCorporateDetailView,
    DsbUserCorporateListView,
)

app_name = "dsb_user_corporate"

urlpatterns = [
    path(
        "dsb-user-corporate/list/",
        DsbUserCorporateListView.as_view(),
        name="dsb-user-corporate-list",
    ),
    re_path(
        r"^dsb-user-corporate/details/$",
        DsbUserCorporateDetailView.as_view(),
        name="dsb-user-corporate-details",
    ),
]
