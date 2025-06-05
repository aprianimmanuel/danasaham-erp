from __future__ import annotations

from split_settings.tools import include  # type: ignore  # noqa: PGH003

include(
    "base.py",
    "logging.py",
    "application.py",
    "auth.py",
    "database.py",
    "security.py",
    "storage.py",
    "rest.py",
    "redis.py",
    "sentry.py",
    "silk.py",
    "spectacular.py",
    "celery.py",
    "cache.py",
    "axes.py",
    "email.py",
    "jwt.py",
    scope=globals(),
)
