import pytest
from celery.contrib.testing.worker import start_worker
from tasks.app import celery_app
from asyncio import new_event_loop
from pytest_asyncio import fixture as async_fixture


pytest_plugins = "celery.contrib.pytest"

@pytest.fixture(scope='session')
def celery_config():
    return {
        'broker_url': 'memory://',
        'result_backend': 'memory://',
    }

@pytest.fixture(scope='session')
def celery_includes():
    return [
        'app.config.dttotDoc.tasks'
    ]

@pytest.fixture(scope='session')
def celery_enable_logging():
    return True

@pytest.fixture(scope='session')
def celery_worker_pool():
    return 'solo'

@pytest.fixture(scope='session')
def celery_worker_parameters():
    return {
        'queues': ('default',),
    }

@pytest.fixture(scope='session')
def celery_session_worker(celery_app, celery_worker_pool, celery_worker_parameters):
    with start_worker(celery_app, pool=celery_worker_pool, **celery_worker_parameters) as worker:
        yield worker

# Define the event loop fixture
@pytest.fixture(scope='function')
def event_loop():
    loop = new_event_loop()
    yield loop
    loop.close()

# Celery app fixture
@pytest.fixture(scope='function')
def celery_app_fixture(celery_config, celery_worker_pool, celery_worker_parameters):
    with celery_app() as app:
        yield app