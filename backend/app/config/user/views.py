from __future__ import annotations

from typing import TYPE_CHECKING, Any

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

from app.common.routers import CustomViewRouter
from app.config.user.serializers import (
    CustomRegisterSerializer,
    CustomUserDetailsSerializer,
)

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.response import Response

router = CustomViewRouter()


class CustomUserDetailsView(BaseUserDetailsView):
    serializer_class = CustomUserDetailsSerializer

    def get(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().get(request, *args, **kwargs)
        response.data.update({"detail": "User details fetched successfully."})
        return response

    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().put(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data.update({"detail": "User details updated successfully."})
        else:
            response.data.update({"detail": "Failed to update user details."})
        return response

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().patch(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data.update({"detail": "User details partially updated successfully."})
        else:
            response.data.update({"detail": "Failed to partially update user details."})
        return response


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_201_CREATED:
            response.data.update({"detail": "User registered successfully."})
        else:
            response.data.update({"detail": "Failed to register user."})
        return response

def custom_url_generator(user: Any, request: Request, temp_key: str) -> str:
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # Use user.pk for the UID
    token = temp_key

    path = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
    return request.build_absolute_uri(path)


class CustomPasswordResetView(DjRestAuthPasswordResetView):

    def get_email_options(self) -> dict[str, Any]:
        """Return the email options including the custom URL generator."""
        return {
            "url_generator": lambda user, request: custom_url_generator(user, request, self.temp_key),
        }

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data.update({"detail": "Password reset email sent successfully."})
        else:
            response.data.update({"detail": "Failed to send password reset email."})
        return response


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
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data.update({"detail": "Password successfully reset."})
        else:
            response.data.update({"detail": "Failed to reset password. Invalid UID or token."})
        return response

# Register the views with the router if not already registered elsewhere
router.register_decorator(r"users/details/", name="user-details", view=CustomUserDetailsView)
router.register_decorator(r"users/register/", name="user-register", view=CustomRegisterView)
router.register_decorator(r"users/password/reset/", name="password-reset", view=CustomPasswordResetView)
router.register_decorator(r"users/password/reset/confirm/", name="password-reset-confirm", view=CustomPasswordResetConfirmView)
