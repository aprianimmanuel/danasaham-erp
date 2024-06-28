from __future__ import annotations

from asyncio import new_event_loop
from os import getenv

import pytest
from celery.contrib.testing.worker import start_worker

from tasks.app import celery_app

pytest_plugins = "celery.contrib.pytest"


@pytest.fixture(scope="session")
def celery_config():
    return {
        "broker_url": getenv("CELERY_BROKER_URL"),
        "result_backend": getenv("CELERY_RESULT_BACKEND"),
        "task_always_eager": False,
        "task_serializer": "json",
        "result_serializer": "json",
        "accept_content": ["json"],
        "task_track_started": True,
        "track_started": True,
    }


@pytest.fixture(scope="session")
def celery_includes():
    return ["app.config.dttotDoc.tasks", "app.config.dsb_user_personal.tasks"]


@pytest.fixture(scope="session")
def celery_enable_logging() -> bool:
    return True


@pytest.fixture(scope="session")
def celery_worker_pool() -> str:
    return "solo"


@pytest.fixture(scope="session")
def celery_worker_parameters():
    return {
        "queues": ("default",),
        "perform_ping_check": False,
    }


@pytest.fixture(scope="session")
def celery_parameters():
    return {
        "broker_url": getenv("CELERY_BROKER_URL"),
        "result_backend": getenv("CELERY_RESULT_BACKEND"),
        "task_always_eager": False,
        "worker_max_tasks_per_child": 1,
    }


@pytest.fixture(scope="session")
def use_celery_app_trap() -> bool:
    return True


@pytest.fixture(scope="session")
def celery_session_worker(
    celery_session_app,
    celery_worker_pool,
    celery_worker_parameters,
):
    with start_worker(
        celery_session_app,
        pool=celery_worker_pool,
        **celery_worker_parameters,
    ) as worker:
        yield worker


# Define the event loop fixture
@pytest.fixture(scope="session")
def event_loop():
    loop = new_event_loop()
    yield loop
    loop.close()


# Celery app fixture
@pytest.fixture()
def celery_function_app_fixture(
    celery_config,
    celery_worker_pool,
    celery_worker_parameters,
):
    with celery_app() as app:
        yield app
