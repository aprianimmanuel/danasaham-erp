from __future__ import annotations

import logging

import pandas as pd
from celery import chain, shared_task

from app.config.core.models import Document, User
from app.config.log_tracker_corporate.tasks import (
    process_log_tracker_corporate_document,
)
from app.config.log_tracker_personal.tasks import process_log_tracker_personal_document
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
        document_process_log_tracker_publisher_document = Document.objects.get(document_id=document_id)
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

        # Replace NaN values with None
        df = df.replace(  # noqa: PD901
            {pd.NaT: None},
        )

        # Save data to the model
        save_data_to_model(
            df,
            user_process_log_tracker_publisher_document,
            document_process_log_tracker_publisher_document,
        )

        # Log the processing information
        logger.info("Document %s is being processed.", document_process_log_tracker_publisher_document.pk)

    except Document.DoesNotExist:
        logger.exception("Document %s does not exist.", document_id)
        raise
    except User.DoesNotExist:
        logger.exception("User %s does not exist.", user_id)
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
        process_log_tracker_personal_document.si(user_data_serializable, document_data_serializable),
        process_log_tracker_corporate_document.si(user_data_serializable, document_data_serializable),
    )()
