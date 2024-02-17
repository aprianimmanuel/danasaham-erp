from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_email.models import EmailDevice
from user.serializers import (UserSerializer,
                              AuthTokenSerializer,
                              VerifyTOTPSecretSerializer)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django_otp import devices_for_user

User = get_user_model()


# User Creation View
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user.generate_totp_secret()


class LoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer
    if api_settings.DEFAULT_RENDERER_CLASSES:
        renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES

        def post(self, request, *args, **kwargs):
            serializer = self.serializer_class(data=request.data,
                                               context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']

            # Check if user has an email device set up
            if user_has_device(user, confirmed=True, model=EmailDevice):
                device = EmailDevice.objects.filter(user=user,
                                                    confirmed=True).first()
                if device:
                    device.generate_challenge()
                    return Response(
                        {
                            'message':
                            'Please check your email for the verification code.'  # noqa
                        },
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {
                            'error': 'Email OTP Device Setup is required'
                        }, status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Fallback or error handling if no email device is set up
                return Response(
                    {
                        'error': 'No OTP Device found for the user.'
                    }, status=status.HTTP_400_BAD_REQUEST
                )


# User Management View
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# Generate MFA Token View
class GenerateMFATokenView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user_has_device(user):
            device = TOTPDevice.objects.create(user=user)
            device.save()
            return Response(
                {
                    'message': 'MFA device setup initiated.',
                    'device_id': device.persistent_id},
                status=status.HTTP_200_OK
                )  # noqa

        device = TOTPDevice.objects.filter(user=user).first()
        if device:
            token = device.generate_token()
            return Response({'token': token}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'MFA device setup is required.'}, status=status.HTTP_400_BAD_REQUEST)  # noqa


# Generate TOTP Secret View
class GenerateTOTPSecretView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        TOTPDevice.objects.create(user=user, confirmed=True)
        return Response({'message': 'TOTP secret generated successfully'})


# Verify TOTP Secret View
class VerifyTOTPSecretView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = VerifyTOTPSecretSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            user = request.user
            is_valid = False
            for device in devices_for_user(user):
                if device.verify_token(token):
                    is_valid = True
                    break
            if is_valid:
                return Response({'is_valid': True}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {'is_valid': False}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Setup Email OTP View
class SetupEmailOTPView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        # Check if the user already has an EmailDevice
        if not EmailDevice.objects.filter(user=user, confirmed=False).exists():
            # Create and save a new EmailDevice for the user
            device = EmailDevice.objects.create(user=user, confirmed=False)
            # Generate a challenge (token) and send it to the user's email
            device.generate_challenge()
            return Response(
                {
                    'message':
                    'Email OTP device setup completed'
                },
                status=status.HTTP_201_CREATED)
        else:
            return Response(
                {
                    'error':
                    'An Email OTP setup process is already in progress or completed.'  # noqa
                },
                status=status.HTTP_400_BAD_REQUEST
            )
