from django.db import transaction
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from django_otp import devices_for_user, user_has_device
from user.serializers import (UserSerializer,
                              AuthTokenSerializer,
                              VerifyTOTPSecretSerializer)
from rest_framework.authtoken.views import ObtainAuthToken
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django_otp.plugins.otp_email.models import EmailDevice


User = get_user_model()


# User Creation View
class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # OTP setup and verification logic is handled within the serializer
            return Response({
                "user_id": user.user_id,
                "email": user.email,
                "username": user.username,
                "email_verified": user.email_verified,
                "message": "User created successfully. Please check your email to verify."  # noqa
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyTOTPSecretSerializer(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            otp = serializer.validated_data['token']
            email = request.data.get('email')

            user = User.objects.filter(email=email).first()
            if not user:
                return Response(
                    {"error": "User not found."},
                    status=status.HTTP_404_NOT_FOUND)

            device = EmailDevice.objects.filter(
                user=user, confirmed=False).first()
            if device and device.verify_token(otp):
                device.confirmed = True
                device.save()
                user.email_verified = True
                user.save()
                return Response(
                    {"message": "Email verified successfully."},
                    status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "Invalid OTP or OTP expired."},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    lookup_field = 'user_id'

    def get_object(self):
        pk = self.kwargs.get('pk')
        user = get_object_or_404(User, pk=pk)
        self.check_object_permissions(self.request, user)
        return user


class LoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Email verification check
            if not user.email_verified:
                return Response(
                    {
                        "error": "Email not verified. Please verify your email first."  # noqa
                        },
                    status=status.HTTP_401_UNAUTHORIZED)

            # Handling different actions
            action = request.data.get('action', '')
            if action == 'login':
                return self.process_login(request, user)
            elif action == 'verify_totp':
                return self.process_verify_totp(request, user)
            else:
                # Default behavior for login if no specific action is provided
                return super(LoginView, self).post(request, *args, **kwargs)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)

    def process_login(self, request, user):
        if user_has_device(
            user,
            confirmed=True,
        ):
            device = devices_for_user(
                user,
                confirmed=True,
            )
            if device:
                extra_context = {
                    'username': user.username,
                    'email': device.email if device.email else user.email
                }
                device.generate_challenge(extra_context=extra_context)
                return Response(
                    {
                        'message': 'Please check your email for the verification code.'  # noqa
                    }, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        'error': 'Email OTP device setup is required'
                    }, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {
                    'error': 'No OTP Device found for the user.'
                }, status=status.HTTP_400_BAD_REQUEST
            )

    @transaction.atomic
    def process_verify_totp(self, request, user):
        serializer = VerifyTOTPSecretSerializer(data=request.data)
        if serializer.is_valid():
            token = serializer.validated_data['token']
            device = devices_for_user(
                user,
                confirmed=True).filter(type='otp_totp.totpdevice')
            if device and device.verify_token(token):
                # Device verification successful, grant access token
                token, _ = Token.objects.get_or_create(user=user)
                return Response(
                    {'token': token.key},
                    status=status.HTTP_200_OK)
            else:
                return Response(
                    {'is_valid': False},
                    status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


# User Management View
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
