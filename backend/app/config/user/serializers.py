from __future__ import annotations

from typing import Any

from dj_rest_auth.registration.serializers import (
    RegisterSerializer as DefaultRegisterSerializer,
)
from dj_rest_auth.serializers import (
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    UserDetailsSerializer,
)
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from app.config.core.models import UserProfile

User = get_user_model()


class CustomUserDetailsSerializer(UserDetailsSerializer):
    first_name = serializers.CharField(source="profile.first_name")
    last_name = serializers.CharField(
        source="profile.last_name",
        required=False,
        allow_null=True,
    )
    username = serializers.CharField(read_only=True)

    class Meta(UserDetailsSerializer.Meta):
        model = User
        fields = (
            *UserDetailsSerializer.Meta.fields,
            "username",
            "first_name",
            "last_name",
        )

    def update(
        self,
        instance: User, # type: ignore  # noqa: PGH003
        validated_data: dict[str, Any],
    ) -> User: # type: ignore  # noqa: PGH003
        """To update the user instance with the validated data.

        Args:
        ----
            instance (User): The user instance to update.
            validated_data (dict[str, Any]): The validated data for updating the user.

        Returns:
        -------
            User: The updated user instance.

        """
        profile_data = validated_data.pop("profile", {})
        first_name = profile_data.get("first_name")
        last_name = profile_data.get("last_name")

        # Update UserProfile instance
        # We use update_or_create here to ensure that the UserProfile instance
        # is created if it doesn't exist, and updated if it does.
        UserProfile.objects.update_or_create(
            user=instance,
            defaults={"first_name": first_name, "last_name": last_name},
        )

        # Update other user fields
        # We call the super method to update the other user fields.
        return super().update(instance, validated_data)


class CustomRegisterSerializer(DefaultRegisterSerializer):
    def validate_email(self, email: str) -> str:
        existing = User.objects.filter(email__iexact=email).exists()
        if existing:
            msg = "A user with that email already exists."
            raise serializers.ValidationError(msg)
        return super().validate_email(email)

    def validate_username(self, username: str) -> str:
        """To validate the username field.

        Args:
        ----
            username (str): The username to validate.

        Returns:
        -------
            str: The validated username.

        Raises:
        ------
            serializers.ValidationError: If a user with the username already exists.

        """
        existing = User.objects.filter(username__iexact=username).exists()
        if existing:
            msg = "A user with that username already exists."
            raise serializers.ValidationError(msg)
        return super().validate_username(username)

class CustomPasswordResetSerializer(PasswordResetSerializer):
    """To customize the password reset serializer."""

    def get_email_options(
        self,
    ) -> dict[str, Any]:
        """To Override email options to use default_token_generator."""
        return {
            "uid": lambda user: urlsafe_base64_encode(force_bytes(user.pk)),
            "token": lambda user: default_token_generator.make_token(user),
        }

    def validate_email(
            self,
            value: str,
    ) -> str:
        """To ensure the email is valid and associated with a user."""
        try:
            self.user = User.objects.get(email__iexact=value)
        except User.DoesNotExist:
            msg = _("No user associated with this email address.")
            raise serializers.ValidationError(msg)  # noqa: B904
        return value

    def save(
            self,
    ) -> None:
        """To save the password reset token to the user."""
        request = self.context.get("request")
        email = self.validated_data["email"]

        # Ensure the user exists before proceeding
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(  # noqa: B904
                _("No user associated with this email address."),
            )

        # Generate password reset token and uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Send the email with the reset URL
        reset_url = request.build_absolute_uri(
            f"/password_reset/confirm/{uid}/{token}/",
        )

        # Send email logic
        self.send_reset_email(user, reset_url)

    def send_reset_email(
            self,
            user: Any,
            reset_url: str,
    ) -> None:
        """To send the password reset email."""
        subject = "Password Reset Requested"
        message = f"Hello,\n\nPlease click the link below to reset your password:\n\n{reset_url}"
        user.email(subject, message)

class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    """To customize the password reset confirm serializer."""

    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    def validate(
            self,
            attrs: Any,
    ) -> Any:
        """To validate the password reset confirm serializer."""
        uid = attrs.get("uid")
        token = attrs.get("token")
        new_password1 = attrs.get("new_password1")
        new_password2 = attrs.get("new_password2")

        # Decode the UID and the retrieve the user
        try:
            uid_decoded = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=uid_decoded)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            msg = "Invalid UID"
            raise serializers.ValidationError(  # noqa: B904
                msg,
            )

        # Check the validity of the token
        if not default_token_generator.check_token(user, token):
            msg = "Invalid token or token expired"
            raise serializers.ValidationError(
                msg,
            )

        # Check if the new passwords match
        if new_password1 != new_password2:
            msg = "The new passwords do not match"
            raise serializers.ValidationError(
                msg,
            )

        # Check password validity
        if not self.validate_password_strength(new_password1):
            msg = "The new password is not strong enough"
            raise serializers.ValidationError(
                msg,
            )

        # Store the user instance and new password for later saving
        self.user = user
        self.new_password1 = new_password1
        return attrs

    def validate_password_strength(
        self,
        password: str,
    ) -> bool:
        """Add custom password strength validation."""
        return bool(any(char.isdigit() for char in password) and any(not char.isalpha() for char in password))

    def save(
            self,
        ) -> Any:
        """Once validation passes, set the new password for the user."""
        user = self.user
        new_password1 = self.new_password

        user.set_password(new_password1)
        user.save()

        return user


class MessageSerializer(serializers.Serializer):
    detail = serializers.CharField()
