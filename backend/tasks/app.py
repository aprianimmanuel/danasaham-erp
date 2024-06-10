from __future__ import annotations

from celery import Celery

from app.config import celery as config

app = Celery("main")
app.config_from_object(config)
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')