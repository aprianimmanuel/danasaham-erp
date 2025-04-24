from __future__ import annotations

import logging
from typing import Any

from django.conf import settings  #type: ignore # noqa: PGH003
from django.conf.urls.static import static  #type: ignore # noqa: PGH003
from django.contrib import admin  #type: ignore # noqa: PGH003
from django.shortcuts import redirect  #type: ignore # noqa: PGH003
from django.urls import include, path  #type: ignore # noqa: PGH003
from drf_spectacular.utils import extend_schema  #type: ignore # noqa: PGH003
from drf_spectacular.views import (  #type: ignore # noqa: PGH003
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (  #type: ignore # noqa: PGH003
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from app.config.silk import USE_SILK  #type: ignore # noqa: PGH003
from app.config.storage import (  #type: ignore # noqa: PGH003
    USE_S3_FOR_MEDIA,
    USE_S3_FOR_STATIC,
)

logger = logging.getLogger(__name__)

# Swagger and Redoc URL patterns
_swagger_urlpatterns = [
    path(
        "api/v1/schema/",
        extend_schema(exclude=True)(SpectacularAPIView).as_view(),
        name="schema",
    ),
    path(
        "docs/",
        extend_schema(exclude=True)(SpectacularSwaggerView).as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "redoc/",
        extend_schema(exclude=True)(SpectacularRedocView).as_view(url_name="schema"),
        name="redoc",
    ),
]


def trigger_error(_request: Any) -> None:
    division_by_zero = 1 / 0


# Main URL patterns
urlpatterns = [
    *_swagger_urlpatterns,
    path("", lambda _request: redirect("docs/"), name="home"),
    path("admin/", admin.site.urls),
    # JWT URLs
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # DRF Spectacular for API schema and documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="api-schema"),
        name="api-docs",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="api-schema"),
        name="api-redoc",
    ),
    # Include other app URLs
    path("", include("app.user.urls")),
    path("", include("app.documents.urls")),
    path("", include("app.documents.dttotDoc.urls")),
    path("", include("app.dsb_user.dsb_user_personal.urls")),
    path("", include("app.dsb_user.dsb_user_corporate.urls")),
    path("", include("app.dsb_user.dsb_user_publisher.urls")),
    path("", include("app.documents.dttotDoc.dttotDocReport.urls")),
    path("", include("app.documents.dttotDoc.dttotDocReportPersonal.urls")),
    path("", include("app.documents.dttotDoc.dttotDocReportPublisher.urls")),
    path("", include("app.documents.dttotDoc.dttotDocReportCorporate.urls")),
    path("accounts/", include("allauth.urls")),
    path("sentry-debug/", trigger_error),
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
