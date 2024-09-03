from __future__ import annotations

import logging

from celery import chain, shared_task

from app.config.core.models import Document, User, log_tracker_publisher
from app.config.log_tracker_publisher.utils.utils import (
    fetch_data_from_external_db,
    save_data_to_model,
)

logger = logging.getLogger(__name__)


@shared_task()
def process_log_tracker_publisher_document(
    user_id: str,
    document_id: str,
) -> None:
    """Process Log Tracker Publisher document.

    This function fetches data from the external database, saves it to the model,
    and updates the document status.

    Args:
    ----
        document_id (str): The ID of the document to process.
        user_id (str): The ID of the user to process.

    Raises:
    ------
        Document.DoesNotExist: If the document associated with the Log Tracker Publisher instance does not exist.
        User.DoesNotExist: If the user does not exist.

    """
    try:
        # Get the document and user objects
        document_process_log_tracker_publisher_document = Document.objects.get(pk=document_id)
        user_process_log_tracker_publisher_document = User.objects.get(pk=user_id)

        # Retrieve the Document instance
        if not document_process_log_tracker_publisher_document:
            msg = "Document ID not found in context"
            raise ValueError(msg)

        # Retrieve the User instance
        if not user_process_log_tracker_publisher_document:
            msg = "User ID not found in context"
            raise ValueError(msg)

        # Fetch data from the external database
        df = fetch_data_from_external_db()  # noqa: PD901

        # Save data to the model
        save_data_to_model(
            df,
            document_process_log_tracker_publisher_document,
            user_process_log_tracker_publisher_document,
        )

        # Log the processing information
        logger.info("Document %s is being processed.", log_tracker_publisher.pk)

    except log_tracker_publisher.DoesNotExist:
        logger.exception("Log Tracker Publisher doesn't exist: %s", log_tracker_publisher.pk)
        raise
    except Document.DoesNotExist:
        logger.exception("Document %s does not exist.", Document.pk)
        raise
    except User.DoesNotExist:
        logger.exception("User %s does not exist.", User.pk)
        raise

@shared_task()
def initiate_log_tracker_publisher(
    user_data_serializable: str,
    document_data_serializable: str,
) -> None:
    logger.info("Initiating Log Tracker Publisher for document %s", document_data_serializable)

    # Create a chain of tasks
    task_chain = chain(
        process_log_tracker_publisher_document.si(user_data_serializable, document_data_serializable),
    )()
