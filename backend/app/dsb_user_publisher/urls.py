from __future__ import annotations

from django.urls import path, re_path  #type: ignore # noqa: PGH003

from app.dsb_user_publisher.views import (  #type: ignore # noqa: PGH003
    DsbUserPublisherDetailView,
    DsbUserPublisherListView,
)

app_name = "dsb_user_publisher"

urlpatterns = [
    path(
        "api/dsb-user-publisher/list/",
        DsbUserPublisherListView.as_view(),
        name="dsb-user-publisher-list",
    ),
    re_path(
        r"^api/dsb-user-publisher/details/$",
        DsbUserPublisherDetailView.as_view(),
        name="dsb-user-publisher-details",
    ),
]
