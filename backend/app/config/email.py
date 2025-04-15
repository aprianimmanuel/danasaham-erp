from __future__ import annotations

import os
import pathlib

from dotenv import load_dotenv

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

load_dotenv(str(BASE_DIR / ".env"))

EMAIL_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_POSTFIX_HOST = os.getenv("EMAIL_HOST")
EMAIL_HOST_PORT = os.getenv("EMAIL_HOST_PORT")


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = EMAIL_POSTFIX_HOST
EMAIL_PORT = EMAIL_HOST_PORT
EMAIL_HOST_USER = EMAIL_USER
EMAIL_HOST_PASSWORD = EMAIL_PASSWORD
EMAIL_USE_TLS = True

SITE_ID = 1

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_AUTHENTICATION_METHOD = "username_email"
