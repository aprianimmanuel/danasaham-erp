from __future__ import annotations

import logging
from typing import Any

from django.db import transaction  #type: ignore  # noqa: PGH003
from django.db.models.signals import post_save  #type: ignore  # noqa: PGH003
from django.dispatch import Signal, receiver  #type: ignore  # noqa: PGH003

from app.documents.models import Document  #type: ignore  # noqa: PGH003

logger = logging.getLogger(__name__)


document_created = Signal(
    providing_args=[
        "instance",
        "created",
        "context",
        "user_data",
        "document_data",
    ],
)


@receiver(post_save, sender=Document)
def trigger_document_processing(
    sender: type['Document'],
    instance: 'Document',
    created: bool,
    **kwargs: Any,
) -> None:
    """Signal handler for Document post_save signal.

    Dispatches processing for newly created 'DTTOT Report' documents.
    """

    if not created:
        return

    try:
        if instance.document_type == "DTTOT Report":
            context = kwargs.get("context", {})
            user = instance.created_by
            user_data = str(user.user_id) if user else "unknown"
            document_data = str(instance.pk)

            transaction.on_commit(
                lambda: document_created.send_robust(
                    sender=instance.__class__,
                    instance=instance,
                    created=created,
                    context=context,
                    user_data=user_data,
                    document_data=document_data,
                )
            )

            logger.info(
                f"Triggered processing for Document {instance.pk} by user {user_data} with context {context}",
            )
        else:
            logger.info(
                f"Document {instance.pk} created with non-DTTOT type '{instance.document_type}', no processing triggered.",
            )

    except Exception as e:
        logger.error(
            f"Error in trigger_document_processing for Document {instance.pk}: {e}",
            exc_info=True,  # biar stacktrace-nya ikut ke log
        )