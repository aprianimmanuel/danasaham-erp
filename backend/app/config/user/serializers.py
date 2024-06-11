from dj_rest_auth.serializers import UserDetailsSerializer
from rest_framework import serializers
from app.config.core.models import UserProfile
from dj_rest_auth.registration.serializers import RegisterSerializer as DefaultRegisterSerializer  # noqa
from django.contrib.auth import get_user_model


User = get_user_model()


class CustomUserDetailsSerializer(UserDetailsSerializer):
    first_name = serializers.CharField(source="profile.first_name")
    last_name = serializers.CharField(
        source="profile.last_name",
        required=False,
        allow_null=True)
    username = serializers.CharField(
        read_only=True
    )

    class Meta(UserDetailsSerializer.Meta):
        model = User
        fields = UserDetailsSerializer.Meta.fields + (
            'username',
            'first_name',
            'last_name',)

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile', {})
        first_name = profile_data.get('first_name')
        last_name = profile_data.get('last_name')

        # Update UserProfile instance
        UserProfile.objects.update_or_create(
            user=instance, defaults={
                'first_name': first_name, 'last_name': last_name
            }
        )

        # Update other user fields
        return super().update(instance, validated_data)


class CustomRegisterSerializer(DefaultRegisterSerializer):
    def validate_email(self, email):
        existing = User.objects.filter(email__iexact=email).exists()
        if existing:
            raise serializers.ValidationError(
                "A user with that email already exists.")
        return super().validate_email(email)

    def validate_username(self, username):
        existing = User.objects.filter(username__iexact=username).exists()
        if existing:
            raise serializers.ValidationError(
                "A user with that username already exists.")
        return super().validate_username(username)
