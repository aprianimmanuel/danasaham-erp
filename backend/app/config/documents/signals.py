from __future__ import annotations

import logging
from typing import Any

from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver

from app.config.core.models import Document

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
    instance: Any,
    created: bool,  # noqa: FBT001
    **kwargs: Any,
) -> None:
    """Signal handler for Document post_save signal.

    When a new Document is created, it dispatches signals for further processing.

    Args:
    ----
        sender (Type[Document]): The sender of the signal.
        instance (Document): The instance of the document being saved.
        created (bool): A boolean indicating if the document was created.
        **kwargs: Additional keyword arguments.

    Returns:
    -------
        None

    """
    # Check if the document was created and if its type is "DTTOT Report"
    if created and instance.document_type == "DTTOT Report":
        context = kwargs.get("context", {})
        # Get the context from kwargs, otherwise use an empty dictionary
        user = instance.created_by
        user_data = str(user.user_id)
        document_data = str(instance.pk)

        # Get the user who created the document
        transaction.on_commit(
        # Create a dictionary with the user's ID
            lambda: document_created.send_robust(
        # Wrap the sending of the signal in a transaction.on_commit()
        # to ensure that the signal is sent after the document is saved
                sender=instance.__class__,
                instance=instance,
                created=created,
                context=context,
                user_data=user_data,
                document_data=document_data,
            ),
        )
