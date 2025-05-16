from __future__ import annotations

import asyncio
import pytest
from django.conf import settings
from unittest import mock

from tasks.app import celery_app

from django.db import transaction

from typing import TYPE_CHECKING, Any
import contextlib
import os


if TYPE_CHECKING:
    from celery.app.task import Task


# Load default plugins
pytest_plugins = [
    "celery.contrib.pytest",
]

# -------------------------------------
# Session-wide fixtures
# --------------------------------------

@pytest.fixture(scope="session")
def event_loop() -> asyncio.AbstractEventLoop: # type: ignore
    """Create an event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def celery_config() -> dict[str, Any]:
    """Return Celery configuration."""
    return {
        "broker_url": settings.CELERY_BROKER_URL,
        "result_backend": settings.CELERY_RESULT_BACKEND,
        "task_always_eager": False,
        "task_eager_propagates": False,
        "accept_content": ["json"],
        "task_serializer": "json",
        "result_serializer": "json",
        "enable_utc": settings.CELERY_ENABLE_UTC,
        "timezone": settings.CELERY_TIMEZONE,
    }

@pytest.fixture(scope="session")
def celery_includes() -> list[str]:
    """Auto-discover Celery tasks."""
    return [
        # List all celery task modules here
        "app.documents.dttotDoc.tasks",
        "app.dsb_user.dsb_user_corporate.tasks",
        "app.dsb_user.dsb_user_personal.tasks",
        "app.dsb_user.dsb_user_publisher.tasks",
        "app.documents.dttotDoc.dttotDocReport.tasks",
        "app.documents.dttotDoc.dttotDocReportCorporate.tasks",
        "app.documents.dttotDoc.dttotDocReportPersonal.tasks",
        "app.documents.dttotDoc.dttotDocReportPublisher.tasks",
    ]

@pytest.fixture(scope="session")
def celery_enable_logging() -> bool:
    return True

@pytest.fixture(scope="session")
def celery_worker_pool() -> str:
    """Return Celery worker pool."""
    return "solo"

@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {
        "queues": ("default",),
    }


# -------------------------------------
# Mocks for transactions and signals
# --------------------------------------

@pytest.fixture(autouse=True)
def mock_atomic(request):
    """Automatically mock `transaction.atomic` for all tests,
    unless otherwise specified.
    """
    if "disable_mock_atomic" in request.fixturenames:
        yield
    else:
        with mock.patch("django.db.transaction.atomic") as _atomic:
            yield _atomic

@pytest.fixture
def disable_mock_atomic():
    """Fixture to disable mocking of transaction.atomic"""
    with contextlib.ExitStack() as stack:
        yield

# -------------------------------------
# Celery app fixture
# --------------------------------------

@pytest.fixture(scope="session")
def celery_function_app_fixture() -> Any:
    return celery_app

