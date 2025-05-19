from __future__ import annotations

import os
import redis
from django.conf.settings import REDIS_HOST, REDIS_PORT, REDIS_DB


RedisClient = redis.Redis(
    host=os.getenv("REDIS_HOST", REDIS_HOST),
    port=os.getenv("REDIS_PORT", REDIS_PORT),
    db=os.getenv("REDIS_DB", REDIS_DB),
)