from __future__ import annotations

import logging

import pandas as pd
from celery import shared_task

from app.config.core.models import Document, User
from app.config.log_tracker_corporate.utils.utils import (
    fetch_data_from_external_db,
    save_data_to_model,
)

logger = logging.getLogger(__name__)


@shared_task()
def process_log_tracker_corporate_document(
    user_id: str,
    document_id: str,
) -> None:
    """To process Log Tracker Corporate document.

    This function fetches data from the external database, saves it to the model,
    and updates the document status.

    Args:
    ----
        document_id (str): The ID of the document to process.
        user_id (str): The ID of the user to process.

    Raises:
    ------
        Document.DoesNotExist: If the document associated with the Log Tracker Corporate instance does not exist.
        User.DoesNotExist: If the user does not exist.

    """
    try:
        # Get the document and user objects
        document_process_log_tracker_corporate_document = Document.objects.get(pk=document_id)
        user_process_log_tracker_corporate_document = User.objects.get(pk=user_id)


        # Retrieve the Document instance
        if not document_process_log_tracker_corporate_document:
            msg = "Document ID not found in context"
            raise ValueError(msg)

        # Retrieve the User instance
        if not user_process_log_tracker_corporate_document:
            msg = "User ID not found in context"
            raise ValueError(msg)

        # Fetch data from the external database
        df = fetch_data_from_external_db()  # noqa: PD901

        # Replace NaT with None
        df = df.replace(  # noqa: PD901
            {pd.NaT: None},
        )

        # Save data to the model
        save_data_to_model(
            df,
            user_process_log_tracker_corporate_document,
            document_process_log_tracker_corporate_document,
        )

        # Log the processing information
        logger.info(
            "Processed Log Tracker Corporate document: %s",
            document_process_log_tracker_corporate_document.pk,
        )

    except Document.DoesNotExist:
        logger.exception(
            "Document with ID %s does not exist in the Log Tracker Corporate model.",
            document_id,
        )
        raise
    except User.DoesNotExist:
        logger.exception(
            "User with ID %s does not exist in the User model.",
            user_id,
        )
        raise

