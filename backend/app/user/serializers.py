from __future__ import annotations

import logging
import random
import string
from datetime import timedelta
from typing import Any, ClassVar

from dj_rest_auth.registration.serializers import (  #type: ignore # noqa: PGH003
    RegisterSerializer as DefaultRegisterSerializer,
)
from dj_rest_auth.registration.serializers import (  #type: ignore # noqa: PGH003
    VerifyEmailSerializer as DefaultVerifyEmailSerializer,
)
from dj_rest_auth.serializers import (  #type: ignore # noqa: PGH003
    PasswordResetConfirmSerializer,
    PasswordResetSerializer,
    UserDetailsSerializer,
)
from django.contrib.auth.hashers import make_password  #type: ignore # noqa: PGH003
from django.contrib.auth.tokens import (  #type: ignore # noqa: PGH003
    default_token_generator,
)
from django.core.mail import send_mail  #type: ignore # noqa: PGH003
from django.utils import timezone  #type: ignore # noqa: PGH003
from django.utils.crypto import get_random_string  #type: ignore # noqa: PGH003
from django.utils.encoding import force_bytes, force_str  #type: ignore # noqa: PGH003
from django.utils.http import (  #type: ignore # noqa: PGH003
    urlsafe_base64_decode,
    urlsafe_base64_encode,
)
from django.utils.translation import gettext_lazy as _  #type: ignore # noqa: PGH003
from rest_framework import (  #type: ignore # noqa: PGH003
    serializers,
)

from app.user.models import (  #type: ignore # noqa: PGH003
    EmailVerificationCode,
    Profile,
    User,
)

logger = logging.getLogger(__name__)

class CustomUserDetailsSerializer(UserDetailsSerializer):
    first_name = serializers.CharField(source="profile.first_name")
    last_name = serializers.CharField(
        source="profile.last_name",
        required=False,
        allow_null=True,
    )
    phone_number = serializers.CharField(
        source="profile.phone_number",
        allow_null=True,
    )
    bio = serializers.CharField(source="profile.bio", required=False, allow_null=True)
    birth_date = serializers.DateField(
        source="profile.birth_date",
        required=False,
        allow_null=True,
    )
    email_verified = serializers.BooleanField(
        source="email_verified",
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "email_verified",
            "bio",
            "phone_number",
            "birth_date",

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
        bio = profile_data.get("bio")

        # Update UserProfile instance
        Profile.objects.filter(user=instance).update(
            first_name=first_name,
            last_name=last_name,
            bio=bio,
        )

        # Update other user fields
        return super().update(instance, validated_data)


class CustomUserUpdateSensitiveDataSerializer(serializers.ModelSerializer):
    """Update user sensitive data like email, phone_number, username."""

    new_username = serializers.CharField(required=False)
    new_email = serializers.EmailField(required=False)
    new_phone_number = serializers.CharField(required=False)

    class Meta:
        model = User
        fields: ClassVar = [
            "new_username",
            "new_email",
            "new_phone_number",
        ]

    def validate(
        self, attrs: dict[str, Any],
    ) -> dict[str, Any]:
        """To validate the serializer data.

        This method is called when the serializer is validated. It checks
        if the user has changed any of the sensitive fields (username, email,
        phone_number) and if so, generates a verification code and sends it
        to the user.

        Args:
        ----
            attrs (dict[str, Any]): The serializer data.

        Returns:
        -------
            dict[str, Any]: The validated data.

        """
        user = self.instance
        requires_verification = False

        # Check if username is changed
        if "new_username" in attrs and attrs["new_username"] != user.username:
            requires_verification = True

        # Check if email is changed
        if "new_email" in attrs and attrs["new_email"] != user.email:
            requires_verification = True

        # Check if phone_number is changed
        if (
            "new_phone_number" in attrs
            and attrs["new_phone_number"] != user.profile.phone_number
        ):
            requires_verification = True

        if requires_verification:
            # Generate and send verification code
            verification_code = "".join(random.choices(string.digits, k=8))  # noqa: S311
            EmailVerificationCode.objects.update_or_create(
                user=user,
                type_used="Sensitive Data Update",
                status_used=False,
                created_date=timezone.now(),
                verification_code=verification_code,
            )

        return attrs

    def update(
        self, instance: User, validated_data: dict[str, Any],
    ) -> User:
        """Update user if only user has verified this action through email verification.

        Args:
        ----
            instance (User): The user instance to update.
            validated_data (dict[str, Any]): The validated data for updating the user.

        Returns:
        -------
            User: The updated user instance.

        """
        profile = instance.profile

        if "new_username" in validated_data:
            instance.username = validated_data["new_username"]

        if "new_email" in validated_data:
            instance.email = validated_data["new_email"]

        if "new_phone_number" in validated_data:
            profile.phone_number = validated_data["new_phone_number"]
            profile.save()

        instance.save()
        return instance


class CustomRegisterSerializer(DefaultRegisterSerializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    verification_code = serializers.CharField(write_only=True, max_length=8)

    def validate(self, data:dict) -> dict:
        email = data.get("email")
        password = data.get("password1")
        verification_code = data.get("verification_code")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(  # noqa: B904
                {
                    "email": "User with this email does not exist.",
                },
            )

        if not user.check_password(password, user.password):
            raise serializers.ValidationError(
                {
                    "password": "Invalid password.",
                },
            )

        try:
            stored_code = EmailVerificationCode.objects.get(user=user, verification_code=verification_code)
        except EmailVerificationCode.DoesNotExist:
            raise serializers.ValidationError(  # noqa: B904
                {
                    "verification_code": "Invalid verification code.",
                },
            )

        # Check if verification code is expired (valid for 5 minutes)
        if timezone.now() - stored_code.created_date > timedelta(minutes=5):
            raise serializers.ValidationError(
                {
                    "verification_code": "Verification code has expired.",
                },
            )

        user.email_verified = True
        stored_code.status_used = True
        stored_code.updated_date = timezone.now()

        try:
            user.save()
            stored_code.save()
        except Exception as e:
            logger.exception("Failed to update user and verification code. Error: %s", e)  # noqa: TRY401
            raise serializers.ValidationError(  # noqa: B904
                {
                    "error": "Failed to update user and verification code.",
                },
            )
        return data


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

class CustomVerifyEmailSerializer(DefaultVerifyEmailSerializer):
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    verification_code = serializers.CharField(write_only=True, max_length=8)

    def validate(
        self,
        data: dict[str, str],
    ) -> dict[str, str]:
        """Validate the input data and return the validated data.

        The validation includes the following:
        - The passwords must match.
        - The user with the given email address must exist.
        - The verification code associated with the user must match the given verification code.

        Args:
        ----
            data (Dict[str, str]): The input data to be validated.

        Returns:
        -------
            Dict[str, str]: The validated data.

        """
        email = data.get("email")
        password1: Any = data.get("password1")
        password2: Any = data.get("password2")
        username = data.get("username")

        if password1 != password2:
            raise serializers.ValidationError(
                {
                    "password2": _("Passwords do not match"),
                },
            )

        if len(password1) < 10 or not any (char.isupper() for char in password1):  # noqa: PLR2004
            msg = "Password must be at least 10 characters long and contain at least one uppercase letter."
            raise serializers.ValidationError(msg)

        # Check if user already exists
        if User.objects.filter(email=email).exists():
            msg = "User with this email already exists."
            raise serializers.ValidationError(msg)

        # Check if user with given username already exists
        if User.objects.filter(email=email, username=username).exists():
            msg = "User with this username already exists."
            raise serializers.ValidationError(msg)

        # Generate verification code
        verification_code = get_random_string(8, allowed_chars=string.ascii_uppercase + string.digits)

        # Create user
        user = User.objects.create(
            email=email,
            password=make_password(password1),
            username=username,
            is_active=False,
            email_verified=False,
            is_staff=False,
            updated_date=timezone.now(),
            )

        # Check if a verification code was sent in the last minute
        recent_code = EmailVerificationCode.objects.filter(
            user=user,
            status_used=False,
            type_used="User Initial Registration",
            created_date__gte=timezone.now() - timedelta(minutes=1),
        ).first()

        if recent_code:
            # Update existing code
            recent_code.verification_code = verification_code
            recent_code.updated_date = timezone.now()
            recent_code.save(update_fields=["verification_code", "updated_date"])
        else:
            # Create a new verification code entry
            EmailVerificationCode.objects.create(
                user=user,
                verification_code=verification_code,
                status_used=False,
                type_used="User Initial Registration",
                created_date=timezone.now(),
                updated_date=None,
            )

        # Send verification email
        try:
            send_mail(
                subject="Verify your email",
                message=f"Your verification code is: {verification_code}",
                from_email="no_reply@danasaham.co.id",
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            logger.exception(f"Error sending verification email to {email}: {e}")  # noqa: G004, TRY401
            raise serializers.ValidationError(  # noqa: B904
                {"email": _("Failed to send verification email. Please try again later.")},
            )

        return data



