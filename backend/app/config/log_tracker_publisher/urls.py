from __future__ import annotations

from django.urls import path, re_path

from app.config.log_tracker_publisher.views import (
    LogTrackerPublisherDetailView,
    LogTrackerPublisherListView,
)

app_name = "log_tracker_publisher"

urlpatterns = [
    path(
        "api/documents/log-tracker-publisher/list/",
        LogTrackerPublisherListView.as_view(),
        name="log-tracker-publisher-list",
    ),
    re_path(
        r"^api/documents/log-tracker-publisher/details/$",
        LogTrackerPublisherDetailView.as_view(),
        name="log-tracker-publisher-details",
    ),
]
