from __future__ import annotations

from django.urls import path

from app.config.dsb_user_publisher.views import (
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
    path(
        "api/dsb-user-publisher/details/<uuid:dsb_user_publisher_id>/",
        DsbUserPublisherDetailView.as_view(),
        name="dsb-user-publisher-details",
    ),
]
