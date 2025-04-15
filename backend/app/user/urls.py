from __future__ import annotations

from dj_rest_auth.registration.views import (  #type: ignore # noqa: PGH003
    ResendEmailVerificationView,
)
from dj_rest_auth.views import (  #type: ignore # noqa: PGH003
    LoginView,
    LogoutView,
    PasswordChangeView,
)
from django.urls import path  #type: ignore  # noqa: PGH003

from app.user.views import (  #type: ignore  # noqa: PGH003
    CustomPasswordResetConfirmView,
    CustomPasswordResetConfirmwithTokenView,
    CustomPasswordResetView,
    CustomRegisterView,
    CustomUserDetailsView,
    UserUpdateSensitiveDataView,
    VerifyEmailView,
)

app_name = "user"

urlpatterns = [
    path("profile/", CustomUserDetailsView.as_view(), name="user-details"),
    path("register/", CustomRegisterView.as_view(), name="user-register"),
    path("password/reset/", CustomPasswordResetView.as_view(), name="password-reset"),
    path(
        "password/reset/confirm/",
        CustomPasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
    path("verify/", VerifyEmailView.as_view(), name="email-verify"),
    path("verify/resend/", ResendEmailVerificationView.as_view(), name="email-verify-resend"),
    path(
        "password/reset/confirm/<uuid:user_id>/<str:token>/",
        CustomPasswordResetConfirmwithTokenView.as_view(),
        name="password-reset-confirm-with-token",
    ),
    # Auth URLs
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path(
        "password/change/",
        PasswordChangeView.as_view(),
        name="rest_password_change",
    ),
    path("profile/update/verify", UserUpdateSensitiveDataView.as_view(), name="user-verify-update"),
]
