from __future__ import annotations

import logging
from os import getenv
from typing import Any

from django.core.cache import cache  # type: ignore  # noqa: PGH003

from redis.exceptions import RedisError  # type: ignore  # noqa: PGH003

logger = logging.getLogger(__name__)

USE_REDIS_FOR_CACHE = getenv("USE_REDIS_FOR_CACHE", default="true").lower() == "true"
REDIS_HOST = getenv("REDIS_HOST", "redis")
REDIS_PORT = getenv("REDIS_PORT", "6379")
REDIS_DB = getenv("REDIS_DB", "0")
REDIS_URL = getenv("REDIS_URL", default=f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")


CACHES: dict[str, Any] = {}

# Check if we are running tests
IS_TESTING = getenv("DJANGO_TESTING", default="false").lower() == "true"

if USE_REDIS_FOR_CACHE and not IS_TESTING:
    logger.info("Using Redis for cache")
    CACHES["default"] = {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }

    # Ping the cache to see if it's working
    try:
        cache.set("ping", "pong")

        if cache.get("ping") != "pong":
            msg = "Cache is not working properly."
            raise ValueError(msg)  # noqa: TRY301

        cache.delete("ping")

        logger.info("Cache is working properly")
    except (ValueError, RedisError):
        logger.exception("Cache is not working. Using dummy cache instead")
        CACHES["default"] = {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
else:
    logger.warning("Using dummy cache")
    CACHES["default"] = {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
