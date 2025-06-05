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
    **kwargs: Any,
) -> None:
    """Trigger the Celery task to process the document."""
    if not created:
        logger.debug(f"[Signal] Document {instance.pk} created but not 'created=True', skipping.")  # noqa: G004
        return

    try:
        user_data_serializable = kwargs.get("user_data")
        document_data_serializable = kwargs.get("document_data")

        if not user_data_serializable or not document_data_serializable:
            logger.warning(
                f"[Signal] Missing user_data or document_data in document_created signal for document {instance.pk}",  # noqa: G004
            )
            return

        logger.info(
            f"[Signal] Triggering initiate_document_processing with user_data={user_data_serializable} "  # noqa: G004
            f"and document_data={document_data_serializable}",
        )

        initiate_document_processing.delay(
            user_data_serializable=user_data_serializable,
            document_data_serializable=document_data_serializable,
        )

    except Exception as e:
        logger.error(  # noqa: G201
            f"[Signal] Failed to process document_created signal for document {instance.pk}: {e}",  # noqa: G004
            exc_info=True,
        )
