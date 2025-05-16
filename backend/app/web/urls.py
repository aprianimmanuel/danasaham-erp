from __future__ import annotations

import os
from django.conf import settings
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

BASE_DIR = settings.BASE_DIR

logger = logging.getLogger(__name__)

class CustomSpectacularSwaggerAPIView(SpectacularSwaggerView):
    template_name = "drf_spectacular/swagger_ui.html"


class CustomSpectacularRedocView(SpectacularRedocView):
    template_name = "drf_spectacular/redoc.html"


# Swagger and Redoc URL patterns
_swagger_urlpatterns = [
    path(
        "api/v1/schema/",
        extend_schema(exclude=True)(SpectacularAPIView).as_view(),
        name="schema",
    ),
    path(
        "api/v1/docs/",
        extend_schema(exclude=True)(CustomSpectacularSwaggerAPIView).as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/redoc/",
        extend_schema(exclude=True)(CustomSpectacularRedocView).as_view(url_name="schema"),
        name="redoc",
    ),
]


def trigger_error(_request: Any) -> None:
    division_by_zero = 1 / 0


# Main URL patterns
urlpatterns = [
    *_swagger_urlpatterns,
    path("api/v1/", lambda _request: redirect("docs/"), name="home"),
    path("api/v1/admin/", admin.site.urls),
    # JWT URLs
    path("api/v1/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/v1/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    # Include other app URLs
    path("api/v1/user/", include("app.user.urls")),
    path("api/v1/documents/", include("app.documents.urls")),
    path("api/v1/documents/dttotdoc/", include("app.documents.dttotDoc.urls")),
    path("api/v1/dsbuser/personal/", include("app.dsb_user.dsb_user_personal.urls")),
    path("api/v1/dsbuser/corporate/", include("app.dsb_user.dsb_user_corporate.urls")),
    path("api/v1/dsbuser/publisher/", include("app.dsb_user.dsb_user_publisher.urls")),
    path("api/v1/documents/dttotdoc/dttotdocreport/", include("app.documents.dttotDoc.dttotDocReport.urls")),
    path("api/v1/documents/dttotdoc/dttotdocreport/personal/", include("app.documents.dttotDoc.dttotDocReportPersonal.urls")),
    path("api/v1/documents/dttotdoc/dttotdocreport/publisher/", include("app.documents.dttotDoc.dttotDocReportPublisher.urls")),
    path("api/v1/documents/dttotdoc/dttotdocreport/corporate/", include("app.documents.dttotDoc.dttotDocReportCorporate.urls")),
    path("api/v1/auth/", include("allauth.urls")),
    path("api/v1/sentry-debug/", trigger_error),
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
