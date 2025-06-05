from __future__ import annotations

from .base import BASE_DIR
import os
from os import getenv

from pathlib import Path

from app.config.silk import SILKY_MIDDLEWARE_CLASS, USE_SILK

PROJECT_NAME = getenv("PROJECT_NAME", "danasaham_erp").strip("'\"")
PROJECT_VERBOSE_NAME = getenv("PROJECT_VERBOSE_NAME", "Django Template").strip("'\"")

ENVIRONMENT = getenv("ENVIRONMENT", "local").strip("'\"")
HOST = getenv("HOST", "localhost").strip("'\"")

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.admindocs",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django_celery_beat",
    "axes",
    "silk",
    "django_celery_results",

    # 3rd-party
    "rest_framework",
    "rest_framework.authtoken",
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "dj_rest_auth.registration",
    "allauth.socialaccount",
    "drf_spectacular",
    "drf_spectacular_sidecar",
    "drf_yasg",

    # Local
    "app.user.apps.UserConfig",
    "app.core.apps.CoreConfig",
    "app.documents.apps.DocumentsConfig",
    "app.documents.dttotDoc.apps.DttotDocConfig",
    "app.dsb_user.apps.DsbUserConfig",
    "app.dsb_user.dsb_user_personal.apps.DsbUserPersonalConfig",
    "app.dsb_user.dsb_user_corporate.apps.DsbUserCorporateConfig",
    "app.dsb_user.dsb_user_publisher.apps.DsbUserPublisherConfig",
    "app.documents.dttotDoc.dttotDocReport.apps.DttotDocReportConfig",
    "app.documents.dttotDoc.dttotDocReportPersonal.apps.DttotDocReportPersonalConfig",
    "app.documents.dttotDoc.dttotDocReportPublisher.apps.DttotDocReportPublisherConfig",
    "app.documents.dttotDoc.dttotDocReportCorporate.apps.DttotDocReportCorporateConfig",
    "app.user.user_profile.apps.UserProfileConfig",
    "app.user.user_digital_sign.apps.UserDigitalSignConfig",
    "app.user.user_key_management.apps.UserKeyManagementConfig",
    "app.user.user_signed_document.apps.UserSignedDocumentConfig",

]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    SILKY_MIDDLEWARE_CLASS,
    "axes.middleware.AxesMiddleware",
]

MIDDLEWARE_CLASSES = MIDDLEWARE

if not USE_SILK:
    INSTALLED_APPS.remove("silk")
    MIDDLEWARE.remove(SILKY_MIDDLEWARE_CLASS)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

TEMPLATE_DIRS = [os.path.join(BASE_DIR, "templates")]

TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
    "django.template.loaders.eggs.Loader",
]

ASGI_APPLICATION = "app.web.asgi.application"
WSGI_APPLICATION = "app.web.wsgi.application"
ROOT_URLCONF = "app.web.urls"

LANGUAGE_CODE = getenv("LANGUAGE_CODE", "en-gb")

USE_TZ = True

TIME_ZONE = getenv("TIME_ZONE", "Asia/Jakarta")

USE_I18N = True
