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
    sender: type[Document],  # noqa: ARG001
    instance: Document,
    created: bool,  # noqa: FBT001
    **kwargs: Any,  # noqa: ARG001
) -> None:
    """Signal handler for Document post_save signal.

    Dispatches processing for newly created 'DTTOT Report' documents.
    """
    if not created:
        return

    try:
        if instance.document_type == "DTTOT Report":
            user_id = str(instance.created_by.user_id) if instance.created_by else "unknown"
            document_id = str(instance.pk)

            transaction.on_commit(
                lambda: document_created.send_robust(
                    sender=instance.__class__,
                    instance=instance,
                    created=created,
                    user_data=user_id,
                    document_data=document_id,
                ),
            )

            logger.info(
                f"[Signal] Triggered processing for Document {document_id} by user {user_id}",  # noqa: G004
            )
        else:
            logger.info(
                f"[Signal] Document {instance.pk} created with non-DTTOT type '{instance.document_type}', no processing triggered.",  # noqa: G004
            )

    except Exception as e:
        logger.error(  # noqa: G201
            f"Error in trigger_document_processing for Document {instance.pk}: {e}",  # noqa: G004
            exc_info=True,
        )
