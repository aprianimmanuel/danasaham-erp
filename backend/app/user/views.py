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

from app.common.routers import CustomViewRouter  #type: ignore # noqa: PGH003


router = CustomViewRouter()



# Register the views with the router if not already registered elsewhere
router.register_decorator(r"register/", name="user-register", view=RegisterView)
router.register_decorator(r"register/verify/", name="user-register-verify", view=VerifyEmailView)
router.register_decorator(r"register/verify/resend", name="user-register-verify-resend", view=ResendEmailVerificationView)
router.register_decorator(r"password/reset/", name="password-reset", view=PasswordResetView)
router.register_decorator(r"password/change/", name="password-change", view=PasswordChangeView)
router.register_decorator(r"password/reset/confirm/", name="password-reset-confirm", view=PasswordResetConfirmView)
router.register_decorator(r"profile/", name="user-profile", view=UserDetailsView)
router.register_decorator(r"login/", name="user-login", view=LoginView)
router.register_decorator(r"logout/", name="user-logout", view=LogoutView)
