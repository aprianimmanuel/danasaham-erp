from __future__ import annotations

from dotenv import load_dotenv

from tasks.app import celery_app

load_dotenv()

__all__ = ("celery_app",)
