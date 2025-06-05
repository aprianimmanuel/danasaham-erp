from __future__ import annotations

AUTH_USER_MODEL = "user.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

SITE_ID = 1


AUTHENTICATION_METHOD = "username_email"
LOGIN_METHODS = ["email", "username"]
LOGIN_URL = "http://localhost:8000/api/v1/auth/accounts/login/"



USER_MODEL_USERNAME_FIELD = "username"
PASSWORD_MIN_LENGTH = 10
UNIQUE_EMAIL = True