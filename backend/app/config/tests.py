from __future__ import annotations

import os

from split_settings.tools import include  # type: ignore  # noqa: PGH003

include(
    "base.py",
    "logging.py",
    "application.py",
    "auth.py",
    "security.py",
    "storage.py",
    "rest.py",
    "sentry.py",
    "spectacular.py",
    "celery.py",
)

ENVIRONMENT = "testing"

INSTALLED_APPS = [

    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "django_celery_beat",

    # 3rd-party
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",

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
    "app.user.user_otp.apps.UserOTPConfig",
    "app.user.user_digital_sign.apps.UserDigitalSignConfig",
    "app.user.user_key_management.apps.UserKeyManagementConfig",
    "app.user.user_role.apps.UserRoleConfig",
    "app.user.user_signed_document.apps.UserSignedDocumentConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME"),
        "USER": os.getenv("DB_USER"),
        "PASSWORD": os.getenv("DB_PASSWORD"),
        "HOST": "db",
        "PORT": 5432,
        "CONN_MAX_AGE": 0,
        "OPTIONS": {},
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
]

CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
