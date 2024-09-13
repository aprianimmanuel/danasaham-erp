from __future__ import annotations

from django.urls import path, re_path

from app.config.log_tracker_personal.views import (
    LogTrackerPersonalDetailView,
    LogTrackerPersonalListView,
)

app_name = "log_tracker_corporate"

urlpatterns = [
    path(
        "api/documents/log-tracker-corporate/list/",
        LogTrackerPersonalListView.as_view(),
        name="log-tracker-corporate-list",
    ),
    re_path(
        r"^api/documents/log-tracker-corporate/details/$",
        LogTrackerPersonalDetailView.as_view(),
        name="log-tracker-corporate-details",
    ),
]
