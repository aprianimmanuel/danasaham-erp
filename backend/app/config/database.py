from __future__ import annotations

import logging
from os import getenv

import dj_database_url
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Default to PostgreSQL via PgBouncer
_default_db_url = "sqlite:///db.sqlite3"
DB_URL = getenv("DATABASE_URL", default=_default_db_url)

if _default_db_url == DB_URL:
    logger.warning("Using default database url: '%s'", DB_URL)

CONN_MAX_AGE = int(getenv("CONN_MAX_AGE", default="600"))

DATABASES = {
    "default": dj_database_url.parse(
        DB_URL,
        conn_max_age=CONN_MAX_AGE,
        conn_health_checks=True,
    ),
}

# Ensure the DATABASE_URL environment variable is set correctly
if not DATABASES['default']:
    raise ImproperlyConfigured("DATABASE_URL environment variable is not set or is incorrect.")

# Optional: external database configuration if needed
EXTERNAL_DB_NAME = getenv('EXTERNAL_DB_NAME')
EXTERNAL_DB_HOST = getenv('EXTERNAL_DB_HOST')
EXTERNAL_DB_USER = getenv('EXTERNAL_DB_USER')
EXTERNAL_DB_PORT = getenv('EXTERNAL_DB_PORT')
EXTERNAL_DB_PASSWORD = getenv('EXTERNAL_DB_PASSWORD')
EXTERNAL_DB_URL = getenv('EXTERNAL_DB_URL')

if all([EXTERNAL_DB_NAME, EXTERNAL_DB_HOST, EXTERNAL_DB_USER, EXTERNAL_DB_PORT, EXTERNAL_DB_PASSWORD]):
    DATABASES['external'] = {
        "default": dj_database_url.parse(
            EXTERNAL_DB_URL,
            conn_max_age=CONN_MAX_AGE,
            conn_health_checks=True
        )
    }