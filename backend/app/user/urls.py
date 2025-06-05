from __future__ import annotations

from dj_rest_auth.registration.views import (
    RegisterView,
    VerifyEmailView,
    ResendEmailVerificationView,
)
from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    UserDetailsView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordChangeView,
)
from django.views.decorators.csrf import csrf_exempt

from django.urls import path, re_path  #type: ignore  # noqa: PGH003


app_name = "user"


urlpatterns = [
    path("profile/", UserDetailsView.as_view(), name="user-details"),
    path("register/", RegisterView.as_view(), name="user-register"),
    path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("verify/", VerifyEmailView.as_view(), name="email-verify"),
    path("verify/resend/", ResendEmailVerificationView.as_view(), name="email-verify-resend"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm-with-token",
    ),
    # Auth URLs
    path(
        "password/change/",
        PasswordChangeView.as_view(),
        name="rest_password_change",
    ),
    path("login/", LoginView.as_view(), name="user-login"),
    path("logout/", LogoutView.as_view(), name="user-logout"),
]
