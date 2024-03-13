from dj_rest_auth.views import UserDetailsView as BaseUserDetailsView
from user.serializers import (
    CustomUserDetailsSerializer,
    CustomRegisterSerializer)
from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import PasswordResetView as DjRestAuthPasswordResetView
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from dj_rest_auth.views import PasswordResetConfirmView as DjRestAuthPasswordConfirmView  # noqa
from dj_rest_auth.app_settings import api_settings
from rest_framework.permissions import AllowAny


class CustomUserDetailsView(BaseUserDetailsView):
    serializer_class = CustomUserDetailsSerializer


class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer


def custom_url_generator(self, request, temp_key):
    uid = urlsafe_base64_encode(force_bytes(self.user))
    token = temp_key

    path = reverse(
        'password_reset_confirm',
        kwargs={
            'uidb64': uid,
            'token': token
        }
    )
    return request.build_absolute_uri(path)


class CustomPasswordResetView(DjRestAuthPasswordResetView):

    def get_email_options(self):
        """
        Return the email options including the custom URL generator.
        """
        return {
            "url_generator": custom_url_generator,
        }


class CustomPasswordResetConfirmView(DjRestAuthPasswordConfirmView):
    permission_classes = (AllowAny,)
    serializer_class = api_settings.PASSWORD_RESET_CONFIRM_SERIALIZER

    def post(self, request, *args, **kwargs):
        # Call the parent method, which handles the password reset confirmation
        response = super().post(request, *args, **kwargs)
        # Custom response or additional actions after successful password reset
        return response
