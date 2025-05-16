from __future__ import annotations

import redis as r
from app.config.cache import REDIS_DB, REDIS_HOST, REDIS_PORT

redis_client = r.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)