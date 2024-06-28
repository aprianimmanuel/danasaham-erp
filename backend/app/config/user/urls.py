from __future__ import annotations

from django.urls import path

from .views import (
    CustomPasswordResetConfirmView,
    CustomPasswordResetView,
    CustomRegisterView,
    CustomUserDetailsView,
)

app_name = "user"

urlpatterns = [
    path("details/", CustomUserDetailsView.as_view(), name="user-details"),
    path("register/", CustomRegisterView.as_view(), name="user-register"),
    path("password/reset/", CustomPasswordResetView.as_view(), name="password-reset"),
    path(
        "password/reset/confirm/<uuid:user_id>/<str:token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]
