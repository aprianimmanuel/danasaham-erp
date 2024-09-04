from __future__ import annotations

from django.urls import path, re_path

from app.config.log_tracker_personal.views import (
    LogTrackerPersonalDetailView,
    LogTrackerPersonalListView,
)

app_name = "log_tracker_personal"

urlpatterns = [
    path(
        "api/documents/log-tracker-personal/list/",
        LogTrackerPersonalListView.as_view(),
        name="log-tracker-personal-list",
    ),
    re_path(
        r"^api/documents/log-tracker-personal/details/$",
        LogTrackerPersonalDetailView.as_view(),
        name="log-tracker-personal-details",
    ),
]
