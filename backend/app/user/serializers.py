from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext as _
from django_otp import devices_for_user
from django.db import transaction
from django_otp.plugins.otp_email.models import EmailDevice  # noqa
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from core.models import UserProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""
    password2 = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        min_length=8)

    class Meta:
        model = User
        fields = ['user_id',
                  'email',
                  'username',
                  'password',
                  'password2',
                  ]
        extra_kwargs = {
            'password': {
                'write_only': True,
                'min_length': 8,
                'required': False},
            'user_id': {'read_only': True},
            'username': {'required': True}
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
        """Ensure passwords match if they are included in the request."""
        password = data.get('password')
        password2 = data.pop('password2', None)
        if password and password2 and password != password2:
            raise serializers.ValidationError(
                {
                    "password2": _("Passwords must match.")
                    }
                )
        return data

    @transaction.atomic
    def create(self, validated_data):
        import uuid
        user_id = str(uuid.uuid4())
        username = validated_data.get('username')
        email = validated_data.get('email')
        password = validated_data.get('password')

        user = User.objects.create_user(
            user_id=user_id,
            username=username,
            email=email,
            password=password
        )
        user.set_password(validated_data['password'])
        user.save()

        return user

    def update(self, instance, validated_data):
        """Update a user, setting the password correctly and return it"""
        password = validated_data.pop('password', None)
        instance.email = validated_data.get('email', instance.email)
        instance.username = validated_data.get('username', instance.username)

        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_id', 'username', 'email']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = [
            'user',
            'bio',
            'phone_number',
            'birth_date',
            'first_name',
            'last_name']
        extra_kwargs = {
            'user': {'read_only': True}
        }


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
    email = serializers.EmailField(
        required=False,
        help_text="User's email address.")
    token = serializers.CharField(
        required=True,
        max_length=6,
        min_length=6,
        help_text="The OTP token to verify.")
    uidb64 = serializers.CharField(
        required=False,
        help_text="User ID encoded in base64."
    )

    def validate(self, data):
        """
        Validate the OTP token for the given email.
        """
        email = data.get('email')
        token = data.get('token')
        uidb64 = data.get('uidb64')

        if email:
            # OTP verification path
            user = User.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError(
                    {
                        'error': 'User not found.'
                    }
                )

            # Check if the user exists
            user = User.objects.filter(email=email).first()
            if not user:
                raise serializers.ValidationError({"error": "User not found."})

            # Convert generator to list to handle it properly
            devices = list(devices_for_user(user, confirmed=False))

            if not devices:
                raise serializers.ValidationError(
                    {
                        "error": "No OTP device found for the user."
                        }
                    )

            # Check the first device
            device = devices[0]
            if device.verify_token(token):
                device.confirmed = True
                device.save()
                user.email_verified = True
                user.totp_secret_key = token
                user.save()
                return data
            else:
                raise serializers.ValidationError(
                    {
                        "error": "Invalid OTP or OTP expired."
                        }
                    )
        elif uidb64:
            # Email link verification path
            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = User.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                user = None

            if user and default_token_generator.check_token(user, token):
                user.email_verified = True
                user.save()
                return data
            else:
                raise serializers.ValidationError(
                    {
                        "error": "Invalid token or user does not exist."
                    }
                )
        else:
            raise serializers.ValidationError({"error": "Invalid request."})

        return data
