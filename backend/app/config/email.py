from __future__ import annotations

import os
import pathlib

from dotenv import load_dotenv


BASE_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

load_dotenv(str(BASE_DIR / ".env"))


EMAIL_BACKEND = "app.core.emailbackends.CustomTLSBackend"
EMAIL_HOST =  os.getenv("EMAIL_POSTFIX_HOST")
EMAIL_PORT = os.getenv("EMAIL_HOST_PORT")
EMAIL_HOST_USER = os.getenv("EMAIL_USER")
EMAIL_HOST_PASSWORD = ""
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False

EMAIL_SUBJECT_PREFIX = "[danasaham-erp]"
EMAIL_VERIFICATION_SUPPORT_RESEND = True
EMAIL_NOTIFICATIONS = True
EMAIL_REQUIRED = True
EMAIL_VERIFICATION = "mandatory"
DEFAULT_FROM_EMAIL = os.getenv("EMAIL_USER")