from __future__ import annotations

from django.urls import path, re_path  #type: ignore  # noqa: PGH003

from app.dsb_user.dsb_user_personal.views import (  #type: ignore  # noqa: PGH003
    DsbUserPersonalDetailView,
    DsbUserPersonalListView,
)

app_name = "dsb_user_personal"

urlpatterns = [
    path(
        "api/dsb-user-personal/list/",
        DsbUserPersonalListView.as_view(),
        name="dsb-user-personal-list",
    ),
    re_path(
        r"^api/dsb-user-personal/details/$",
        DsbUserPersonalDetailView.as_view(),
        name="dsb-user-personal-details",
    ),
]
