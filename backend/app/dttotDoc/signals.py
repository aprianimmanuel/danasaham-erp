from __future__ import annotations

import logging
from typing import Any

from django.dispatch import receiver  #type: ignore # noqa: PGH003

from app.documents.signals import document_created  #type: ignore # noqa: PGH003
from app.dttotDoc.tasks import (  #type: ignore # noqa: PGH003
    initiate_document_processing,
)

logger = logging.getLogger(__name__)


@receiver(document_created)
def process_document_signal(
    sender: type[Any],  # noqa: ARG001
    instance: Any,
    created: bool,  # noqa: FBT001
    context: Any,  # noqa: ARG001
    **kwargs: Any,
) -> None:
    """Trigger the Celery task to process the document."""
    if created:
        logger.debug(f"Received document_created signal for {instance.pk}")  # noqa: G004

        # Extract user_data and document_data from kwargs
        user_data_serializable = kwargs.get("user_data")
        document_data_serializable = kwargs.get("document_data")

        # Initiate document processing with the required IDs
        initiate_document_processing.delay(
            user_data_serializable=user_data_serializable,
            document_data_serializable=document_data_serializable,
        )
