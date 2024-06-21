from __future__ import annotations

import logging

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.shortcuts import redirect
from django.urls import include, path
from drf_spectacular.utils import extend_schema
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView
)

from dj_rest_auth.registration.views import VerifyEmailView, ResendEmailVerificationView
from dj_rest_auth.views import LoginView, LogoutView, PasswordChangeView

from rest_framework_simplejwt.views import TokenVerifyView, TokenObtainPairView, TokenRefreshView

from app.config.silk import USE_SILK
from app.config.storage import USE_S3_FOR_MEDIA, USE_S3_FOR_STATIC

from app.config.user.views import (
    CustomRegisterView,
    CustomPasswordResetView
)



logger = logging.getLogger(__name__)

# Swagger and Redoc URL patterns
_swagger_urlpatterns = [
    path(
        "api/v1/schema/",
        extend_schema(exclude=True)(SpectacularAPIView).as_view(),
        name="schema"),
    path(
        "docs/",
        extend_schema(exclude=True)(SpectacularSwaggerView).as_view(url_name="schema"),
        name="swagger-ui"),
    path(
        "redoc/",
        extend_schema(exclude=True)(SpectacularRedocView).as_view(url_name="schema"),
        name="redoc"),
]

def trigger_error(request):
    division_by_zero = 1 / 0

# Main URL patterns
urlpatterns = [
    *_swagger_urlpatterns,
    path('', lambda _request: redirect("docs/"), name="home"),
    path('admin/', admin.site.urls),

    # Auth URLs
    path('api/user/login/', LoginView.as_view(), name='rest_login'),
    path('api/user/logout/', LogoutView.as_view(), name='rest_logout'),
    path('api/user/password/change/', PasswordChangeView.as_view(), name='rest_password_change'),
    path('api/registration/', CustomRegisterView.as_view(), name='rest_register'),
    path('api/registration/user/verify-email/', VerifyEmailView.as_view(), name='rest_verify_email'),
    path('api/registration/user/resend-email/', ResendEmailVerificationView.as_view(), name='rest_resend_verify'),
    path('api/user/password/reset/', CustomPasswordResetView.as_view(), name='rest_password_reset'),

    # User-specific URLs
    path('api/user/', include('app.config.user.urls')),

    # JWT URLs
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),

    # DRF Spectacular for API schema and documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='api-schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='api-schema'), name='api-docs'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='api-schema'), name='api-redoc'),

    # Include other app URLs
    path('', include('app.config.documents.urls')),
    path('', include('app.config.dttotDoc.urls')),
    path('', include('app.config.dsb_user_personal.urls')),
    path('accounts/', include('allauth.urls')),

    path('sentry-debug/', trigger_error),
]


# Conditional inclusion of Silk URLs
if USE_SILK:
    urlpatterns.append(path("silk/", include("silk.urls")))

# Static and media file handling
if not USE_S3_FOR_STATIC:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if not USE_S3_FOR_MEDIA:
    logger.warning("S3 is disabled, serving media files locally. Consider using S3.")
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
