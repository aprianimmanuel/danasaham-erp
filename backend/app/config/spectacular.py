from __future__ import annotations

from app import __version__
from app.config.application import PROJECT_VERBOSE_NAME

SPECTACULAR_SETTINGS = {
    "TITLE": PROJECT_VERBOSE_NAME,
    "SCHEMA_PATH_PREFIX": r"/api/v[0-9]",
    "COMPONENT_SPLIT_REQUEST": True,
    "VERSION": __version__,
}