from __future__ import annotations

from django.urls import path

from app.config.dsb_user_personal.views import (
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
    path(
        "api/dsb-user-personal/details/<uuid:dsb_user_personal_id>/",
        DsbUserPersonalDetailView.as_view(),
        name="dsb-user-personal-details",
    ),
]
