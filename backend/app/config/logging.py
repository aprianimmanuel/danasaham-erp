from __future__ import annotations

import logging.config
from os import getenv

LOG_LEVEL = getenv("LOG_LEVEL", default="INFO")

LOGGING_CONFIG = None

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(asctime)s %(log_color)s%(levelname)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "standard": {
                "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "colored",
            },
            "file": {
                "class": "logging.FileHandler",
                "filename": "debug.log",
                "formatter": "standard",
            },
        },
        "loggers": {
            "django": {
                "handlers": ["console", "file"],
                "level": LOG_LEVEL,
                "propagate": True,
            },
            "celery": {
                "handlers": ["console", "file"],
                "level": LOG_LEVEL,
                "propagate": True,
            },
            "app": {
                "handlers": ["console", "file"],
                "level": LOG_LEVEL,
                "propagate": True,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
        },
    },
)
