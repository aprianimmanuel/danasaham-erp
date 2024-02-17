from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _
from django_otp import match_token
from django.db import transaction
from django_otp.plugins.otp_email.models import EmailDevice
from django_otp import devices_for_user

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""
    password2 = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        min_length=8)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def validate_email(self, value):
        """
        Validate the email field
        """
        if not value:
            raise serializers.ValidationError(_('Email is required'))
        try:
            validate_email(value)
        except DjangoValidationError:
            raise serializers.ValidationError(_('Invalid email address'))
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(_('Email is already in use.'))
        return value

    def validate_username(self, value):
        """
        Validate the username field.
        """
        if not value:
            raise serializers.ValidationError(_('Username is required.'))
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(_('Username is already in use.'))
        if ' ' in value or '#' in value:
            raise serializers.ValidationError(_(
                'Username cannot contain space or special characters'))
        return value

    def validate_password(self, value):
        """
        Validate the password field.
        """
        if not value:
            raise serializers.ValidationError(_('Password is required'))
        if len(value) < 8:
            raise serializers.ValidationError(_(
                'Password must be at least 8 characters long'))
        return value

    def validate(self, data):
        """Ensure passwords match."""
        if data['password'] != data.pop('password2'):
            raise serializers.ValidationError(
                {
                    "password2": _("Passwords must match.")
                }
            )
        return data

    def create(self, validated_data):
        """Create a new user with encrypted password and return it."""
        return User.objects.create_user(**validated_data)


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token, including OTP verification."""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False)

    @transaction.atomic
    def validate(self, attrs):
        """
        Validate and authenticate the user,
        including OTP verification if provided.
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            if not user:
                msg = _(
                    'Unable to authenticate with provided credentials.'
                )
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs

class VerifyTOTPSecretSerializer(serializers.Serializer):
    token = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text="The OTP token to verify.")

    def validate_token(self, value):
        """
        You can add additional validation for the token here if needed.
        For example, you could check if the token only contains digits.
        """
        if not value.isdigit():
            raise serializers.ValidationError("Token must be a 6-digit number.")
        return value

# class OTPVerifySerializer(serializers.Serializer):
#     """Serializer for OTP Verification"""
#     otp_token = serializers.CharField(max_length=6, write_only=True)

#     def validate_otp_token(self, value):
#         """
#         Validate the OTP token againts the user's registered devices.
#         """
#         request = self.context.get('request')
#         user = request.user if request else None
#         if user and not match_token(user, value):
#             raise serializers.ValidationError(_("Invalid OTP token."))
#         return value


# def user_has_email_device(user):
#     """
#     Check if the user has an Email OTP device.

#     Args:
#         user: The user to check for an Email OTP device.

#     Returns:
#         A boolean indicating whether an Email OTP device exists for the user.
#     """  # noqa

#     # Use confirmed=True to check for confirmed devices only
#     devices = devices_for_user(user, confirmed=None)
#     for device in devices:
#         if isinstance(device, EmailDevice):
#             return True
#     return False


# class SetupEmailOTPSerializer(serializers.Serializer):
#     email = serializers.EmailField(
#         required=False,
#         allow_blank=True
#     )

#     def validate(self, attrs):
#         if 'email' not in attrs or not attrs['email']:
#             attrs['email'] = self.context['request'].user.email
#         return attrs

#     def validate_email(self, value):
#         """
#         Custom validation for the email field to ensure it's either provided
#         or the user's email will be used.
#         """
#         if not value:
#             # If no email is provided, default to the user's email
#             value = self.context['request'].user.email
#         else:
#             try:
#                 validate_email(value)
#             except DjangoValidationError:
#                 raise serializers.ValidationError(
#                     "Invalid email address."
#                 )

#         # Check if the email is already associated with an Email Device
#         user = self.context['request'].user
#         if EmailDevice.objects.filter(
#             user=user,
#             email=value
#         ).exists():
#             raise serializers.ValidationError(
#                 'Email is already associated with another Email OTP device.'
#             )

#         # Domain restriction
#         allowed_domains = ["example.com"]
#         domain = value.split('@')[-1]
#         if domain not in allowed_domains:
#             raise serializers.ValidationError(
#                 "Email must belong to a valid domain."
#                 )

#         # User email match check (if applicable)
#         if value and value != user.email:
#             raise serializers.ValidationError(
#                 "The provided email does not match your registered email."
#                 )

#         # Check user email if unique
#         if user_has_email_device(user, value):
#             raise serializers.ValidationError(
#                 "User already has an Email OTP device."
#             )
#         return value
