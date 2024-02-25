from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers, status
from django.utils.translation import gettext as _
from django_otp import devices_for_user
from django.db import transaction
from django_otp.plugins.otp_email.models import EmailDevice
import datetime

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""
    password2 = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        min_length=8)
    otp = serializers.CharField(
        write_only=True,
        required=False,
        help_text="OTP for email_verification"
    )

    class Meta:
        model = User
        fields = ['user_id',
                  'email',
                  'username',
                  'password',
                  'password2',
                  'otp']
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 8},
            'user_id': {'read_only': True}
            }

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

    @transaction.atomic
    def create(self, validated_data):
        otp = validated_data.pop('otp', None)
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()

        return user


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


class VerifyEmailOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, help_text="User's email address.")
    token = serializers.CharField(required=True, max_length=6, min_length=6, help_text="The OTP token to verify.")

    def validate(self, data):
        """
        Validate the OTP token for the given email.
        """
        email = data.get('email')
        token = data.get('token')

        # Check if the user exists
        user = User.objects.filter(email=email).first()
        if not user:
            raise serializers.ValidationError({"error": "User not found."})

        # Convert generator to list to handle it properly
        devices = list(devices_for_user(user, confirmed=False))

        if not devices:
            raise serializers.ValidationError({"error": "No OTP device found for the user."})

        # Assuming check the first device only as an example
        device = devices[0]
        if device.verify_token(token):
            # If OTP is valid, confirm the device and mark email as verified
            device.confirmed = True
            device.save()
            user.email_verified = True
            user.save()
            return data
        else:
            raise serializers.ValidationError({"error": "Invalid OTP or OTP expired."})

        return data
