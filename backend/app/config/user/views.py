from __future__ import annotations

from typing import Any

from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import PasswordResetConfirmView
from dj_rest_auth.views import PasswordResetView as DjRestAuthPasswordResetView
from dj_rest_auth.views import UserDetailsView as BaseUserDetailsView
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from app.common.routers import CustomViewRouter
from app.config.user.serializers import (
    CustomRegisterSerializer,
    CustomUserDetailsSerializer,
)


class CustomUserDetailsView(BaseUserDetailsView):
    serializer_class = CustomUserDetailsSerializer


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


def custom_url_generator(self: Any, request: Request, temp_key: str) -> str:
    uid = urlsafe_base64_encode(force_bytes(self.user))
    token = temp_key

    path = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
    return request.build_absolute_uri(path)


class CustomPasswordResetView(DjRestAuthPasswordResetView):

    def get_email_options(self) -> dict[str, Any]:
        """Return the email options including the custom URL generator."""
        return {
            "url_generator": custom_url_generator,
        }


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    permission_classes = (AllowAny,)
    serializer_class = api_settings.PASSWORD_RESET_CONFIRM_SERIALIZER

    @extend_schema(
        summary="Confirm password reset with UID and token",
        description="This endpoint confirms a password reset based on a user ID (UID) and a security token.",
        responses={
            status.HTTP_200_OK: OpenApiExample(
                "Password successfully reset",
                summary="Successful Reset",
                value={"detail": "Password successfully reset."},
                response_only=True,
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiExample(
                "Invalid UID or token",
                summary="Invalid Request",
                value={"detail": "Invalid UID or token."},
                response_only=True,
            ),
        },
    )
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return super().post(request, *args, **kwargs)


router = CustomViewRouter()
router.register("details", CustomUserDetailsView, name="user-details")
router.register("register", CustomRegisterView, name="user-register")
router.register("password/reset", CustomPasswordResetView, name="password-reset")
router.register(
    "password/reset/confirm/<uuid:user_id>/<str:token>/",
    CustomPasswordResetConfirmView,
    name="password-reset-confirm",
)
