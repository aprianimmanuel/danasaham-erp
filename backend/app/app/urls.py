from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from dj_rest_auth.registration.views import (
    VerifyEmailView,
    ResendEmailVerificationView)
from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView)
from user.views import (
    CustomUserDetailsView,
    CustomRegisterView,
    CustomPasswordResetView)

# JSON Web Token Authentiction
from rest_framework_simplejwt.views import TokenVerifyView
from dj_rest_auth.jwt_auth import get_refresh_view

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),

    # Auth URLs previously in dj-rest-auth
    path('api/user/login/', LoginView.as_view(), name='rest_login'),
    path('api/user/logout/', LogoutView.as_view(), name='rest_logout'),
    path(
        'api/user/password/change/',
        PasswordChangeView.as_view(), name='rest_password_change'),
    path(
        'api/registration/',
        CustomRegisterView.as_view(), name='rest_register'),
    path(
        'api/registration/user/verify-email/',
        VerifyEmailView.as_view(),
        name='rest_verify_email'),
    path(
        'api/registration/user/resend-email/',
        ResendEmailVerificationView.as_view(),
        name='rest_resend_verify'),
    path(
        'api/user/password/reset/',
        CustomPasswordResetView.as_view(),
        name='rest_password_reset'),

    # Include other auth URLs
    path('accounts/', include('allauth.urls')),

    # User-specific URLs
    path(
        'api/user/details/',
        CustomUserDetailsView.as_view(),
        name='rest_details'),

    # JWT URLs if you're using JWT authentication
    path(
        'api/token/verify/',
        TokenVerifyView.as_view(),
        name='token_verify'),
    path(
        'api/token/refresh/',
        get_refresh_view().as_view(),
        name='token_refresh'),

    # DRF spectacular for API schema and documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path(
        'api/docs/',
        SpectacularSwaggerView.as_view(
            url_name='api-schema'
        ),
        name='api-docs'),

    # DTTOT Document API and any other app-specific URLs
    path('api/dttotdoc/', include('dttotDoc.urls')),

    # Custom password reset confirm URL
    path(
        'api/user/password/reset/confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]
