from __future__ import annotations

from asyncio import new_event_loop
from os import getenv
from typing import TYPE_CHECKING, Any

import pytest
from celery.contrib.testing.worker import start_worker  #type: ignore # noqa: PGH003

from tasks.app import celery_app

if TYPE_CHECKING:
    from celery.app.task import Task  #type: ignore # noqa: PGH003

pytest_plugins = "celery.contrib.pytest"


@pytest.fixture(scope="session")
def celery_config() -> dict[str, Any]:
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
def celery_includes() -> list[str]:
    return [
        "app.documents.dttotDoc.tasks",
        "app.dsb_user.dsb_user_personal.tasks",
        "app.documents.dttotDoc.dttotDocReportPublisher.tasks",
        "app.documents.dttotDoc.dttotDocReportPersonal.tasks",
        "app.documents.dttotDoc.dttotDocReportCorporate.tasks",
        "app.documents.dttotDoc.dttotDocReport.tasks",
        "app.dsb_user.dsb_user_corporate.tasks",
        "app.dsb_user.dsb_user_publisher.tasks",
    ]


@pytest.fixture(scope="session")
def celery_enable_logging() -> bool:
    return True


@pytest.fixture(scope="session")
def celery_worker_pool() -> str:
    return "solo"


@pytest.fixture(scope="session")
def celery_worker_parameters() -> dict[str, Any]:
    return {
        "queues": ("default",),
        "perform_ping_check": False,
    }


@pytest.fixture(scope="session")
def celery_parameters() -> dict[str, Any]:
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
    celery_session_app: Task,
    celery_worker_pool: str,
    celery_worker_parameters: dict[str, Any],
) -> Task:
    with start_worker(
        celery_session_app,
        pool=celery_worker_pool,
        **celery_worker_parameters,
    ) as worker:
        yield worker


# Define the event loop fixture
@pytest.fixture(scope="session")
def event_loop() -> Any:
    loop = new_event_loop()
    yield loop
    loop.close()


# Celery app fixture
@pytest.fixture
def celery_function_app_fixture() -> Task:
    with celery_app() as app:
        yield app
