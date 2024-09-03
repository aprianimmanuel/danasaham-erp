from __future__ import annotations

import logging
from typing import Any

from django.dispatch import receiver

from app.config.documents.signals import log_tracker_initiated
from app.config.log_tracker_publisher.tasks import initiate_log_tracker_publisher

logger = logging.getLogger(__name__)


@receiver(log_tracker_initiated)
def initiate_log_tracker_publisher_signal(
    sender: type[Any],  # noqa: ARG001
    instance: Any,
    created: bool,  # noqa: FBT001
    context: Any,  # noqa: ARG001
    **kwargs: Any,
) -> None:
    """Trigger the Celery task to process the document."""
    if created:
        logger.debug(f"Received log_tracker_initiated signal for {instance.pk}")  # noqa: G004

        # Extract user_data and document_data from kwargs
        user_data_serializable = kwargs.get("user_data")
        document_data_serializable = kwargs.get("document_data")

        # Initiate document processing with the required IDs
        initiate_log_tracker_publisher.delay(
            user_data_serializable=user_data_serializable,
            document_data_serializable=document_data_serializable,
        )
