from __future__ import annotations

import os
import redis
from django.conf import settings


RedisClient = redis.Redis(
    host=os.getenv("REDIS_HOST", settings.REDIS_HOST),
    port=os.getenv("REDIS_PORT", settings.REDIS_PORT),
    db=os.getenv("REDIS_DB", settings.REDIS_DB),
)