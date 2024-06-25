from __future__ import annotations

import logging
import os
from os import getenv
from typing import Any, cast
from storages.backends.s3boto3 import S3Boto3Storage
from app.config.base import BASE_DIR


logger = logging.getLogger(__name__)


USE_S3_FOR_MEDIA = getenv("USE_S3_FOR_MEDIA", "false").lower() == "true"
USE_S3_FOR_STATIC = getenv("USE_S3_FOR_STATIC", "false").lower() == "true"

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = "static/"

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = "media/"

AWS_STORAGE_BUCKET_NAME = getenv("AWS_STORAGE_BUCKET_NAME", "bucket")
AWS_S3_CUSTOM_DOMAIN = getenv("AWS_S3_CUSTOM_DOMAIN", f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com")
AWS_S3_ENDPOINT_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}"

AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID", "access_key")
AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY", "secret_key")
AWS_DEFAULT_ACL = None  # Recommended setting for S3
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',
}

AWS_S3_FILE_OVERWRITE = False
AWS_QUERYSTRING_AUTH = False  # Can be set to True if you want to use query string authentication

class CustomDomainS3Storage(S3Boto3Storage):
    """Extend S3 with signed URLs for custom domains."""
    custom_domain = False

    def url(self, name: str, parameters: Any = None, expire: Any = None, http_method: Any = None) -> str:
        """Replace internal domain with custom domain for signed URLs."""
        url = super().url(name, parameters, expire, http_method)
        return url.replace(f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com", AWS_S3_ENDPOINT_URL)

STORAGES: dict[str, Any] = {}

if USE_S3_FOR_STATIC:
    logger.info("Serving static files from S3")
    STORAGES["staticfiles"] = {
        "BACKEND": "app.config.storages.CustomDomainS3Storage",
    }
else:
    logger.info("Serving static files locally")
    STORAGES["staticfiles"] = {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }

if USE_S3_FOR_MEDIA:
    logger.info("Serving media files from S3")
    STORAGES["default"] = {
        "BACKEND": "app.config.storages.CustomDomainS3Storage",
    }
else:
    logger.info("Serving media files locally")
    STORAGES["default"] = {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "LOCATION": MEDIA_ROOT,
        "BASE_URL": MEDIA_URL,
    }
