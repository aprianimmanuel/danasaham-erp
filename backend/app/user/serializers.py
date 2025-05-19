from __future__ import annotations

import re
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
from django.contrib.auth.hashers import make_password, check_password  #type: ignore # noqa: PGH003
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
from app.user.user_otp.models import UserOTP, OTPType
from django.utils.translation import gettext_lazy as _  #type: ignore # noqa: PGH003
from rest_framework import (  #type: ignore # noqa: PGH003
    serializers,
)

from app.user.models import User
from app.user.user_otp.models import UserOTP
from app.user.user_profile.models import UserProfile
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from app.user.user_session.models import UserSession, UserSessionType, UserSessionStatus
from app.core.redisclient import RedisClient


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
    is_email_verified = serializers.BooleanField(
        source="user.is_email_verified",
        read_only=True,
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "is_email_verified",
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
        UserProfile.objects.filter(user=instance).update(
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
        user_profile = user.profile
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
            and attrs["new_phone_number"] != user_profile.phone_number
        ):
            requires_verification = True

        if requires_verification:
            # Generate and send verification code
            verification_code = "".join(random.choices(string.digits, k=10))  # noqa: S311
            UserOTP.objects.update_or_create(
                user=user,
                otp_type=OTPType.EMAIL_VERIFICATION,
                status_used=False,
                created_date=timezone.now(),
                updated_date=None,
                otp_code=verification_code,
                expires_at=timezone.now() + timezone.timedelta(minutes=5),
                default={
                    "otp_code": verification_code,
                    "expires_at": timezone.now + timezone.timedelta(minutes=5),
                    "pending_changes": {
                        "new_username": attrs.get("new_username"),
                        "new_email": attrs.get("new_email"),
                        "new_phone_number": attrs.get("new_phone_number"),
                    },
                },
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


class CustomRegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    email = serializers.EmailField()
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Username is already taken.")
        return username

    def validate_email(self, email):
        allowed_domains = [".com", ".co.id", ".id", ".co"]
        if not any(email.endswith(d) for d in allowed_domains):
            raise serializers.ValidationError("Email domain must be .com, .co.id, .id, or .co")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise serializers.ValidationError("Invalid email format")

        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("This email is already registered")

        return email

    def validate(self, data):
        password1 = data.get("password1")
        password2 = data.get("password2")
        email = data.get("email")

        if password1 != password2:
            raise serializers.ValidationError({"password2": "Passwords do not match"})

        # Cek apakah password pernah dipakai dalam 3 bulan terakhir oleh user yang sama
        three_months_ago = timezone.now() - timedelta(days=90)
        recent_users = User.objects.filter(email=email, updated_date__gte=three_months_ago)
        for user in recent_users:
            if check_password(password1, user.password):
                raise serializers.ValidationError({"password1": "Password was used in the last 3 months"})

        # Validasi kekuatan password
        if len(password1) < 10:
            raise serializers.ValidationError({"password1": "Password must be at least 10 characters long"})
        if not re.search(r"[A-Z]", password1):
            raise serializers.ValidationError({"password1": "Password must contain at least one uppercase letter"})
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password1):
            raise serializers.ValidationError({"password1": "Password must contain at least one special character"})

        return data

    def create(
        self,
        validated_data: dict[str, Any],
    ) -> User:
        """
        Create a new user instance using the validated data.

        Args:
        ----
            validated_data (dict[str, Any]): The validated data for creating a new user.

        Returns:
        -------
            User: The newly created user instance.
        """
        user = User.objects.create(
            email=validated_data["email"],
            username=validated_data["username"],
            password=validated_data["password1"],
            is_email_verified=False,
            is_active=False,
            is_admin=False,
            updated_date=None,
        )

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def _create_user_session(self, user, status: str):
        """Helper to create a user session."""
        UserSession.objects.create(
            user=user,
            session_name=UserSessionType.LOGIN,
            session_status=status,
            last_activity=timezone.now(),
        )

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")

        # Ambil user dari DB untuk catat sesi meskipun auth gagal
        user = User.objects.filter(email=email).first()

        # Cek autentikasi
        authenticated_user = authenticate(
            request=self.context.get("request"), email=email, password=password
        )

        if not authenticated_user:
            if user:
                self._create_user_session(user, UserSessionStatus.FAILED)
            raise AuthenticationFailed("Invalid email or password.")

        if not authenticated_user.is_email_verified:
            self._create_user_session(authenticated_user, UserSessionStatus.FAILED)
            raise AuthenticationFailed("Email is not verified.")

        if not authenticated_user.is_active:
            self._create_user_session(authenticated_user, UserSessionStatus.FAILED)
            raise AuthenticationFailed("User is inactive.")

        # Catat login berhasil
        self._create_user_session(authenticated_user, UserSessionStatus.SUCCESS)

        # Get latest session_id
        latest_session = UserSession.objects.filter(
            user=authenticated_user,
            session_name=UserSessionType.LOGIN,
            session_status=UserSessionStatus.SUCCESS,
        ).latest("last_activity")

        session_id = str(latest_session.session_id)

        # Update last_activity
        latest_session.last_activity = timezone.now()
        latest_session.save(update_fields=["last_activity"])

        # Save to Redis
        RedisClient.setex(
            name=f"user_session:{session_id}",
            time=60 * 60 * 24 * 3,
            value=str(authenticated_user.user_id)
        )

        refresh = RefreshToken.for_user(authenticated_user)
        access = AccessToken.for_user(authenticated_user)

        return {
            "refresh": str(refresh),
            "access": str(access),
            "user_id": authenticated_user.id,
            "email": authenticated_user.email,
            "user_session_id": session_id,
        }


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


class ConfirmEmailVerificationOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    verification_code = serializers.CharField(max_length=10)

    def validate(self, data):
        email = data.get("email")
        code = data.get("verification_code")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "email": "User with this email does not exist.",
                },
            )

        try:
            otp_entry = UserOTP.objects.get(
                user=user,
                otp_code=code,
                otp_type=OTPType.EMAIL_VERIFICATION,
                status_used=False,
                expires_at__gte=timezone.now() - timedelta(minutes=5)
            )
        except UserOTP.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "verification_code": "Invalid or expired verification code",
                },
            )

        data["user"] = user
        data["otp_entry"] = otp_entry
        return data

class UserSensitiveDataOTPVerificationSerializer(serializers.Serializer):
    otp_code = serializers.CharField(max_length=10)

    def validate(self, attrs):
        user = self.context["request"].user
        otp_code = attrs["otp_code"]

        try:
            otp = UserOTP.objects.get(
                user=user,
                otp_code=otp_code,
                otp_type=OTPType.EMAIL_VERIFICATION,
                status_used=False,
                expires_at__gte=timezone.now() - timedelta(minutes=3)
            )
        except UserOTP.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "otp_code": "Invalid or expired verification code",
                },
            )

        # Mark the OTP as used
        attrs["pending_changes"] = otp.pending_changes
        otp.status_used = True
        otp.updated_date = timezone.now()
        otp.save(update_fields=["status_used", "updated_date"])

        return attrs

class ResendEmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {
                    "email": "User with this email does not exists.",
                },
            )

        if user.is_email_verified:
            raise serializers.ValidationError(
                {
                    "email": "Email is already verified.",
                },
            )

        data["user"] = user
        return data

    def create_or_update_otp(self, user):
        verification_code = get_random_string(8, allowed_chars=string.ascii_uppercase + string.digits)

        # Check if an active code exists within the last minute
        recent_code = UserOTP.objects.filter(
            user=user,
            status_used=False,
            otp_type=OTPType.EMAIL_VERIFICATION,
            created_date__gte=timezone.now() - timedelta(minutes=3),
        ).first()

        if recent_code:
            recent_code.otp_code = verification_code
            recent_code.updated_date = timezone.now()
            recent_code.save(update_fields=["verification_code", "updated_date"])
        else:
            UserOTP.objects.create(
                user=user,
                otp_code=verification_code,
                status_used=False,
                otp_type=OTPType.EMAIL_VERIFICATION,
                created_date=timezone.now(),
                updated_date=None,
            )

        # Send the email
        try:
            send_mail(
                subject="Resend: Verify your email",
                message=f"Your new verification code is: {verification_code}",
                from_email="testlab@danasaham.co.id",
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            raise serializers.ValidationError({"email": "Failed to send verification email. Please try again later."})

        return verification_code
