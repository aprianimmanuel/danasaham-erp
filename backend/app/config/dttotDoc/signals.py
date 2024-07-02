from __future__ import annotations

from typing import Any

from django.dispatch import receiver

from app.config.documents.signals import dttot_document_created
from app.config.dttotDoc.tasks import process_dttot_document


@receiver(dttot_document_created)
def process_dttot_document_signal(
    _sender: type[Any],
    instance: Any,
    created: True,
    _context: Any,
    user_data: dict[str, Any],
    **_kwargs: Any,
) -> None:
    if created:
        process_dttot_document.delay(instance.pk, user_data)
