from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django_otp import devices_for_user  # noqa
from user.serializers import (UserSerializer,
                              AuthTokenSerializer,
                              VerifyEmailOTPSerializer)
from rest_framework.authtoken.views import ObtainAuthToken
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django_otp.plugins.otp_email.models import EmailDevice  # noqa


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


# OTP Verification View
class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = VerifyEmailOTPSerializer(data=request.data)
        if serializer.is_valid():
            # If serializer is valid, OTP verification was successful
            return Response(
                {
                    "message": "Email verified successfully."},
                status=status.HTTP_200_OK
            )
        else:
            # If serializer is not valid, return the errors
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, user_id=user_id)
        self.check_object_permissions(self.request, user)
        return user


class LoginView(ObtainAuthToken):
    serializer_class = AuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request})
        if serializer.is_valid():
            user = serializer.validated_data['user']

            # Email verification check
            if not user.email_verified:
                return Response(
                    {"error": "Email not verified. Please verify your email first."},  # noqa
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Generate auth token for successfully authenticated users
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.user_id,
                'email': user.email,
                'username': user.username
            })

        else:
            return Response(
                serializer.errors, status=status.HTTP_401_UNAUTHORIZED)


# User Management View
class ManageUserView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        user = get_object_or_404(User, user_id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def patch(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
