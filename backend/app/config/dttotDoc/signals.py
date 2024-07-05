from __future__ import annotations

import logging
from typing import Any

from django.dispatch import receiver

from app.config.documents.signals import dttot_document_created
from app.config.dttotDoc.tasks import process_dttot_document


logger = logging.getLogger(__name__)

@receiver(dttot_document_created)
def process_dttot_document_signal(
    sender: type[Any],
    instance: Any,
    created: bool,
    context: Any,
    user_data: dict[str, Any],
    **kwargs: Any) -> None:
    if created:
        logger.debug(f"Received dttot_document_created signal for {instance.pk}")
        process_dttot_document.delay(instance.pk, user_data)
