from __future__ import annotations

import logging
from typing import Any

from django.dispatch import receiver  #type: ignore # noqa: PGH003

from app.documents.dttotDoc.tasks import (  #type: ignore # noqa: PGH003
    initiate_document_processing,
)
from app.documents.signals import document_created  #type: ignore # noqa: PGH003

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
        try:
            logger.info(f"[Signal] Received document_created for document {instance.pk}")

            user_data_serializable = kwargs.get("user_data")
            document_data_serializable = kwargs.get("document_data")

            logger.info(
                f"[Signal] Triggering initiate_document_processing with user_data={user_data_serializable} "
                f"and document_data={document_data_serializable}"
            )

            initiate_document_processing.delay(
                user_data_serializable=user_data_serializable,
                document_data_serializable=document_data_serializable,
            )

        except Exception as e:
            logger.error(
                f"[Signal] Failed to process document_created signal for document {instance.pk}: {e}",
                exc_info=True
            )
    else:
        logger.debug(f"[Signal] Document {instance.pk} created but not 'created=True', skipping.")