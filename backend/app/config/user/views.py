from __future__ import annotations

from typing import TYPE_CHECKING, Any

from dj_rest_auth.app_settings import api_settings
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import PasswordResetConfirmView
from dj_rest_auth.views import PasswordResetView as DjRestAuthPasswordResetView
from dj_rest_auth.views import UserDetailsView as BaseUserDetailsView
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny

from app.common.routers import CustomViewRouter
from app.config.user.serializers import (
    CustomPasswordResetConfirmSerializer,
    CustomPasswordResetSerializer,
    CustomRegisterSerializer,
    CustomUserDetailsSerializer,
    MessageSerializer,
)

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.response import Response

router = CustomViewRouter()

def custom_url_generator(user: Any, request: Request, temp_key: str) -> str:
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # Use user.pk for the UID
    token = temp_key

    path = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
    return request.build_absolute_uri(path)

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


class CustomPasswordResetView(DjRestAuthPasswordResetView):
    serializer_class = CustomPasswordResetSerializer

    def get_email_options(
            self,
    ) -> dict[str, Any]:
        """To Override email options to use custom_url_generator."""
        return {
            "uid": lambda user: urlsafe_base64_encode(force_bytes(user.pk)),
            "token": lambda user: custom_url_generator(user, self.request, self.temp_key),
        }

    def post(
            self,
            request: Request,
            *args: Any,
            **kwargs: Any,
    ) -> Response:
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data.update({"detail": "Password reset email sent."})
        else:
            response.data.update({"detail": "Failed to send password reset email."})
        return response

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    permission_classes = (AllowAny,)
    serializer_class = CustomPasswordResetConfirmSerializer

    @extend_schema(
        operation_id="password_reset_confirm",
        summary="Confirm password reset with UID and token",
        description="""
            This endpoint confirms a password reset based on a user ID (UID) and a security token.

            The request body should contain the following fields:
            - `uid`: The user ID (UID) of the user to reset the password for.
            - `token`: The security token to validate the password reset.
            - `new_password1`: The new password for the user.
            - `new_password2`: The new password for the user, repeated for confirmation.
        """,
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=MessageSerializer,
                description="Password successfully reset.",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=MessageSerializer,
                description="Invalid UID or token.",
            ),
        },
    )
    def post(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """To confirm password reset with UID and token.

        This endpoint confirms a password reset based on a user ID (UID) and a security token.

        Args:
        ----
            request (Request): The request object.
            *args (Any): Variable length argument list.
            **kwargs (Any): Arbitrary keyword arguments.

        Returns:
        -------
            Response: The response object.

        Responses:
            200:
                detail (str): Password successfully reset.
            400:
                detail (str): Invalid UID or token.

        """
        response: Response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            response.data.update({"detail": "Password successfully reset."})
        else:
            response.data.update({"detail": "Failed to reset password. Invalid UID or token."})
        return response

class CustomPasswordResetConfirmwithTokenView(PasswordResetConfirmView):
    permission_classes = (AllowAny,)
    serializer_class = CustomPasswordResetConfirmSerializer

    @extend_schema(
        operation_id="password_reset_confirm_with_token",
        summary="Confirm password reset with token",
        description="This endpoint confirms a password reset based on a security token.",
        responses={
            status.HTTP_200_OK: OpenApiResponse(
                response=MessageSerializer,
                description="Password successfully reset.",
            ),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(
                response=MessageSerializer,
                description="Invalid token.",
            ),
        },
    )
    def post(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """To confirm password reset with token.

        This endpoint confirms a password reset based on a security token.

        Args:
        ----
            request (Request): The request object.
            *args (Any): The positional arguments.
            **kwargs (Any): The keyword arguments.

        Returns:
        -------
            Response: The response object.

        Responses:
            200:
                detail (str): Password successfully reset.
            400:
                detail (str): Invalid token.

        """
        # Get the token from the request
        token = request.data.get("token")

        # Check if the token is valid
        if not default_token_generator.check_token(self.user, token):
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

        # Call the parent class's post method
        response = super().post(request, *args, **kwargs)

        if response.status_code == status.HTTP_200_OK:
            response.data.update({"detail": "Password successfully reset."})
        else:
            response.data.update({"detail": "Failed to reset password. Invalid token."})

        return response

# Register the views with the router if not already registered elsewhere
router.register_decorator(r"users/details/", name="user-details", view=CustomUserDetailsView)
router.register_decorator(r"users/register/", name="user-register", view=CustomRegisterView)
router.register_decorator(r"users/password/reset/", name="password-reset", view=CustomPasswordResetView)
router.register_decorator(r"users/password/reset/confirm/", name="password-reset-confirm", view=CustomPasswordResetConfirmView)
