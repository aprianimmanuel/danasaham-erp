from __future__ import annotations

import logging

from celery import shared_task  #type: ignore # noqa: PGH003

from app.documents.models import Document  #type: ignore # noqa: PGH003
from app.dsb_user_corporate.models import (  #type: ignore # noqa: PGH003
    dsb_user_corporate,
)
from app.dsb_user_corporate.utils.utils import (  #type: ignore # noqa: PGH003
    fetch_data_from_external_db,
    save_data_to_model,
)
from app.user.models import User  #type: ignore # noqa: PGH003

logger = logging.getLogger(__name__)


@shared_task()
def process_dsb_user_corporate_document(
    user_id: str,
    document_id: str,
    ) -> None:
    """Process DSB User Corporate document.

    This function fetches data from the external database, saves it to the model,
    and updates the document status.

    Args:
    ----
        document_id (str): The ID of the document to process.
        user_id (str): The ID of the user to process.

    Raises:
    ------
        Document.DoesNotExist: If the document associated with the DSB User Corporate instance does not exist.
        User.DoesNotExist: If the user does not exist.
        Exception: If there is an error processing the document.

    """
    try:
        # Get the document and user objects
        document_process_dsb_corporate_document = Document.objects.get(pk=document_id)
        user_process_dsb_user_corporate_document = User.objects.get(pk=user_id)

        # Retrieve the Document instance
        if not document_process_dsb_corporate_document:
            msg = "Document ID not found in context"
            raise ValueError(msg)

        # Retrieve the User instance
        if not user_process_dsb_user_corporate_document:
            msg = "User ID not found in context"
            raise ValueError(msg)

        # Fetch data from the external database
        data_frame = fetch_data_from_external_db()

        # Save data to the model
        save_data_to_model(data_frame, document_process_dsb_corporate_document, user_process_dsb_user_corporate_document)

        # Log the processing information
        logger.info("Document %s is being processed.", document_process_dsb_corporate_document.pk)

    except dsb_user_corporate.DoesNotExist:
        # Log the error information and raise an exception
        logger.exception("DSB User Corporate document with ID %s does not exist", document_id)
        raise

    except Document.DoesNotExist:
        # Log the error information and raise an exception
        logger.exception("Document with ID %s does not exist", document_id)
        raise
