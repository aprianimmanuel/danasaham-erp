from __future__ import annotations

import logging
import logging.config
import os
import shutil
from os import getenv
from pathlib import Path

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]

# Get log level from environment variable or default to INFO
LOG_LEVEL = getenv("LOG_LEVEL", default="INFO")

# Define log directory and ensure it exists
LOG_DIR = os.path.join(BASE_DIR, "logs", "app")  # noqa: PTH118
os.makedirs(LOG_DIR, exist_ok=True)  # noqa: PTH103

# Define full path for log file
LOG_FILE = os.path.join(LOG_DIR, "app.log")  # noqa: PTH118

# Fix if app.log is a directory or special file
try:
    if os.path.exists(LOG_FILE):  # noqa: PTH110
        if os.path.isdir(LOG_FILE):  # noqa: PTH112
            print(f"[Log Fix] '{LOG_FILE}' is a directory. Removing it...")  # noqa: T201
            shutil.rmtree(LOG_FILE)
        elif not os.path.isfile(LOG_FILE):  # noqa: PTH113
            print(f"[Log Fix] '{LOG_FILE}' is not a regular file. Removing it...")  # noqa: T201
            os.remove(LOG_FILE)  # noqa: PTH107
except OSError as e:
    print(f"[Log Error] Failed to fix log file path: {e}")  # noqa: T201

# Disable Django's default logging config loading
LOGGING_CONFIG = None

# Configure logging with fallback
try:
    logging.config.dictConfig({
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
            "otp_file": {
                "level": LOG_LEVEL,
                "class": "logging.FileHandler",
                "filename": os.path.join(LOG_DIR, "otp.log"),  # noqa: PTH118
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
            "otp_logger": {
                "handlers": ["otp_file"],
                "level": LOG_LEVEL,
                "propagate": True,
            },
        },
        "root": {
            "handlers": ["console", "file"],
            "level": LOG_LEVEL,
        },
    })
except Exception as e:
    print(f"[Log Warning] Failed to load dictConfig: {e}")  # noqa: T201
    logging.basicConfig(
        level=LOG_LEVEL,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )