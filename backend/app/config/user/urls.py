from __future__ import annotations

from django.urls import path

from app.config.user.views import (
    CustomPasswordResetConfirmView,
    CustomPasswordResetConfirmwithTokenView,
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
        "password/reset/confirm/",
        CustomPasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path(
        "password/reset/confirm/<uuid:user_id>/<str:token>/",
        CustomPasswordResetConfirmwithTokenView.as_view(),
        name="password-reset-confirm-with-token",
    ),
]
