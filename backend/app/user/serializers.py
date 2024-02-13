from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """Create a new user with encrypted password and return it"""
        return User.objects.create_user(**validated_data)

    def validate(self, data):
        """Validate all fields"""

        if not data.get('email'):
            raise ValidationError({'email': _('This field may not be blank.')})

        if not data.get('username'):
            raise ValidationError({'username': _('This field may not be blank.')})  # noqa

        if not data.get('password'):
            raise ValidationError({'password': _('This field may not be blank.')})  # noqa

        if User.objects.filter(email=data['email']).exists():
            raise ValidationError({'email': _('User with this email address already exists.')})  # noqa

        if not data['username'].replace('_', '').isalnum():
            raise ValidationError({'username': _('Username can only contain alphanumeric characters and underscores.')})  # noqa

        password = data['password']
        if len(password) < 8:
            raise ValidationError({'password': _('Password must be at least 8 characters long.')})  # noqa

        if not any(char.isupper() for char in password):
            raise ValidationError({'password': _('Password must contain at least one uppercase letter.')})  # noqa

        if not any(char.isdigit() for char in password):
            raise ValidationError({'password': _('Password must contain at least one digit.')})  # noqa

        if not any(char in "!@#$%^&*()-_+=<>,.?/:;{}[]|~" for char in password):  # noqa
            raise ValidationError({'password': _('Password must contain at least one special character.')})  # noqa

        return data


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the user"""
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)  # noqa

            if not user:
                msg = _('Unable to authenticate with provided credentials.')
                raise serializers.ValidationError(msg, code='authentication')

        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
