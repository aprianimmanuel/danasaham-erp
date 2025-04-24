from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, ClassVar

from dj_rest_auth.registration.views import RegisterView  #type: ignore # noqa: PGH003
from dj_rest_auth.views import PasswordResetConfirmView  #type: ignore # noqa: PGH003
from dj_rest_auth.views import (  #type: ignore # noqa: PGH003
    PasswordResetView as DjRestAuthPasswordResetView,
)
from django.contrib.auth.tokens import (  #type: ignore # noqa: PGH003
    default_token_generator,
)
from django.shortcuts import get_object_or_404  #type: ignore # noqa: PGH003
from django.urls import reverse  #type: ignore # noqa: PGH003
from django.utils.encoding import force_bytes  #type: ignore # noqa: PGH003
from django.utils.http import urlsafe_base64_encode  #type: ignore # noqa: PGH003
from drf_spectacular.utils import (  #type: ignore # noqa: PGH003
    OpenApiResponse,
    extend_schema,
)
from rest_framework import generics, status  #type: ignore # noqa: PGH003
from rest_framework.permissions import (  #type: ignore # noqa: PGH003
    AllowAny,
    IsAuthenticated,
)

from app.common.routers import CustomViewRouter  #type: ignore # noqa: PGH003
from app.user.models import User
from app.user.serializers import (  #type: ignore # noqa: PGH003
    CustomPasswordResetConfirmSerializer,
    CustomPasswordResetSerializer,
    CustomRegisterSerializer,
    CustomUserDetailsSerializer,
    CustomUserUpdateSensitiveDataSerializer,
    CustomVerifyEmailSerializer,
    MessageSerializer,
)
from app.user.user_profile.models import UserProfile

if TYPE_CHECKING:
    from rest_framework.request import Request  #type: ignore # noqa: PGH003
    from rest_framework.response import Response  #type: ignore # noqa: PGH003, TCH004

router = CustomViewRouter()

logger = logging.getLogger(__name__)

def custom_url_generator(user: Any, request: Request, temp_key: str) -> str:
    uid = urlsafe_base64_encode(force_bytes(user.pk))  # Use user.pk for the UID
    token = temp_key

    path = reverse("password_reset_confirm", kwargs={"uidb64": uid, "token": token})
    return request.build_absolute_uri(path)

class CustomUserDetailsView(generics.RetrieveUpdateAPIView):
    """Custom User Details View.

    - GET: Retrieve user details by `user_id` or `profile_id`
    - PUT/PATCH: Update `first_name, `last_name` and `bio`by `user_id` or `profile_id`
    """

    serializer_class = CustomUserDetailsSerializer
    permission_classes: ClassVar = [IsAuthenticated]

    def get_object(self, request: Request) -> User:
        """To retrieve user details by `user_id` or `profile_id`.

        **Query Parameters:**

        * `user_id`: The ID of the user to retrieve.
        * `profile_id`: The ID of the profile to retrieve.

        **Returns:**

        * `User`: The retrieved user object.
        """
        user_id = request.query_params.get("user_id")
        profile_id = request.query_params.get("profile_id")

        if user_id:
            logger.info("Fetching user by user_id: %s", user_id)
            user = get_object_or_404(User, id=user_id)
        elif profile_id:
            logger.info("Fetching user by profile_id: %s", profile_id)
            profile = get_object_or_404(UserProfile, id=profile_id)
            user = profile.user
        else:
            logger.warning("user_id or profile_id is required but missing")
            raise Response(
                {
                    "error": "user_id or profile_id is required but missing",
                },
            )

        return user

    def get(
        self,
        request: Request,  # noqa: ARG002
        *args: Any,  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> Response:
        """To retrieve user details.

        This endpoint accepts two query parameters: `user_id` and `profile_id`.
        If `user_id` is provided, the endpoint will retrieve the user object
        using the `id` field. If `profile_id` is provided, the endpoint will
        retrieve the user object using the `profile_id` field.

        **Query Parameters:**

        * `user_id`: The ID of the user to retrieve.
        * `profile_id`: The ID of the profile to retrieve.

        **Returns:**

        * `Response`: A JSON response containing the user details.
        """
        user: User = self.requ
        if not isinstance(user, User):
            return user

        serializer = self.get_serializer(user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def update(
        self,
        request: Request,
        *args: Any,  # noqa: ARG002
        **kwargs: Any,  # noqa: ARG002
    ) -> Response:
        """To Update user profile.

        This endpoint requires a JSON payload with the updated user data.
        The endpoint will update the user profile if the data is valid.
        If the data is invalid, the endpoint will return a 400 Bad Request response.

        **Request Body:**

        * `user`: The user object with the updated fields.
        * `profile`: The profile object with the updated fields.

        **Returns:**

        * `Response`: A JSON response containing the updated user details.
        """
        user: User = self.request.user
        if not isinstance(user, User):
            return user  # Return early if error response

        serializer = self.get_serializer(
            user, data=request.data, partial=request.method == "PATCH",
        )
        if serializer.is_valid():
            serializer.save()
            logger.info("User profile updated successfully for user_id: %s", user.id)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # If the data is invalid, return a 400 Bad Request response
        logger.warning("Failed to update profile for user_id: %s, errors: %s", user.id, serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # noqa: ARG002
        """To inform that Method POST is not allowed.

        Args:
        ----
            request (Request): The request object.
            *args (Any): Additional positional arguments.
            **kwargs (Any): Additional keyword arguments.

        Returns:
        -------
            Response: A 405 Method Not Allowed response.

        """
        logger.warning("Method POST is not allowed for user profile update.")
        return Response({"error": "Method POST is not allowed."}, status=status.HTTP_405_METHOD_NOT_ALLOWED)


class UserUpdateSensitiveDataView(generics.GenericAPIView):
    """View for updating user sensitive data that needs to be verified."""

    serializer_class = CustomUserUpdateSensitiveDataSerializer
    permission_classes: ClassVar = [IsAuthenticated]

    def get_object(self):  # noqa: ANN201
        return self.request.user

    def put(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._update(request, *args, **kwargs)

    def patch(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        return self._update(request, *args, **kwargs)

    def _update(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # noqa: ARG002
        """To help function for handling PUT and PATCH requests."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=self.request.method == "PATCH")
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def perform_update(self, serializer) -> None:  # noqa: ANN001
        serializer.save()


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer
    permission_classes= (AllowAny,)

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # noqa: ARG002
        logger.info("Incoming registation for email: %s", request.data.get("email"))

        serializer = CustomRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(request)
            return Response(
                {
                    "response": "User registered successfully.",
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomPasswordResetView(DjRestAuthPasswordResetView):
    serializer_class = CustomPasswordResetSerializer
    permission_classes = (AllowAny,)

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

class VerifyEmailView(generics.GenericAPIView):
    """View untuk verifikasi email berdasarkan kode verifikasi."""

    serializer_class = CustomVerifyEmailSerializer
    permission_classes: ClassVar = [AllowAny]

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:  # noqa: ARG002
        """To post request for email verification."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get validated data
        validated_data = serializer.validated_data
        email = validated_data.get("email")
        password1 = validated_data.get("password1")
        first_name = validated_data.get("first_name")
        last_name = validated_data.get("last_name")

        # Get user based on email provided
        user = User.objects.get(email=email)
        user_profile = UserProfile.objects.get(user_id=user.user_id)

        # Check if email has been verified before
        if user.is_email_verified:
            return Response(
                {
                    "detail": "Email is already verified.",
                }, status=status.HTTP_400_BAD_REQUEST,
            )

        # Update user data
        user.set_password(password1)
        user_profile.first_name = first_name
        user_profile.last_name = last_name
        user.is_email_verified = False
        user.save()

        return Response(
            {
                "detail": "Account has been created. Please verify your email.",
            },
            status=status.HTTP_200_OK,
        )

# Register the views with the router if not already registered elsewhere
router.register_decorator(r"user/register/", name="user-register", view=CustomRegisterView)
router.register_decorator(r"user/password/reset/", name="password-reset", view=CustomPasswordResetView)
router.register_decorator(r"user/password/reset/confirm/", name="password-reset-confirm", view=CustomPasswordResetConfirmView)
router.register_decorator(r"user/password/reset/confirm/<uuid:user_id>/<str:token>/", name="password-reset-confirm-with-token", view=CustomPasswordResetConfirmwithTokenView)
router.register_decorator(r"user/verify/", name="email-verify", view=VerifyEmailView)
router.register_decorator(r"user/profile/update/verify", name="user-verify-update", view=UserUpdateSensitiveDataView)
router.register_decorator(r"user/profile/", name="user-profile", view=CustomUserDetailsView)

