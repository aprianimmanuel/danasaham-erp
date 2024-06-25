from __future__ import annotations

import os
from pathlib import Path
from datetime import timedelta
from os import getenv
from app.config.silk import SILKY_MIDDLEWARE_CLASS, USE_SILK

PROJECT_NAME = getenv("PROJECT_NAME", "danasaham_erp").strip("'\"")
PROJECT_VERBOSE_NAME = getenv(
    "PROJECT_VERBOSE_NAME", "Django Template").strip("'\"")

ENVIRONMENT = getenv("ENVIRONMENT", "local").strip("'\"")
HOST = getenv("HOST", "localhost").strip("'\"")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',
    'django_celery_beat',
    'axes',
    'silk',
    'rest_framework',
    'rest_framework.authtoken',
    'dj_rest_auth',
    'allauth',
    'allauth.account',
    'dj_rest_auth.registration',
    'allauth.socialaccount',
    'drf_spectacular',
    'app.config.core',
    'app.config.user',
    'app.config.documents',
    'app.config.dttotDoc',
    'app.config.dsb_user_personal',
    'app.config.dttotDocReport',
    'django_celery_results'
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
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
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ASGI_APPLICATION = 'app.web.asgi.application'
WSGI_APPLICATION = 'app.web.wsgi.application'
ROOT_URLCONF = 'app.web.urls'

LANGUAGE_CODE = getenv("LANGUAGE_CODE", "en-us")

USE_TZ = True

TIME_ZONE = getenv("TIME_ZONE", "UTC")

USE_I18N = True