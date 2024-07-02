from __future__ import annotations

import logging.config
from pathlib import Path
from os import getenv
from app.config.base import BASE_DIR

LOG_LEVEL = getenv("LOG_LEVEL", default="INFO")


# Define the logging path
LOG_DIR = Path(BASE_DIR) / "logs"
LOG_FILE = LOG_DIR / "debug.log"

# Ensure the logging directory exists
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE.touch(exist_ok=True)


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
                "level": LOG_LEVEL,
                "class": "logging.FileHandler",
                "filename": LOG_FILE,
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
