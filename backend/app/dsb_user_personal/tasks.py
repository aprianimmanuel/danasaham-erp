from __future__ import annotations

import logging

from celery import shared_task  #type: ignore # noqa: PGH003

from app.documents.models import Document  #type: ignore # noqa: PGH003
from app.dsb_user_personal.models import dsb_user_personal  #type: ignore # noqa: PGH003
from app.dsb_user_personal.utils.utils import (  #type: ignore # noqa: PGH003
    fetch_data_from_external_db,
    save_data_to_model,
)
from app.user.models import User  #type: ignore # noqa: PGH003

logger = logging.getLogger(__name__)


@shared_task()
def process_dsb_user_personal_document(
    user_id: str,
    document_id: str,
) -> None:
    """Process DSB User Personal document.

    This function fetches data from the external database, saves it to the model,
    and updates the document status.

    Args:
    ----
        document_id (str): The ID of the document to process.
        user_id (str): The ID of the user to process.

    Raises:
    ------
        Document.DoesNotExist: If the document associated with the DSB User Personal instance does not exist.
        User.DoesNotExist: If the user does not exist.
        Exception: If there is an error processing the document.

    """
    try:
        # Get the document and user objects
        document_process_dsb_personal_document = Document.objects.get(pk=document_id)
        user_process_dsb_user_personal_document = User.objects.get(pk=user_id)

        # Retrieve the Document instance
        if not document_process_dsb_personal_document:
            msg = "Document ID not found in context"
            raise ValueError(msg)  # noqa: TRY301

        # Retrieve the User instance
        if not user_process_dsb_user_personal_document:
            msg = "User ID not found in context"
            raise ValueError(msg)  # noqa: TRY301

        # Fetch data from the external database
        df = fetch_data_from_external_db()  # noqa: PD901

        # Save data to the model
        save_data_to_model(df, document_process_dsb_personal_document, user_process_dsb_user_personal_document)

        # Log the processing information
        logger.info("Document %s is being processed.", dsb_user_personal.pk)

    except dsb_user_personal.DoesNotExist:
        # Log the error information if the DSB User Personal instance does not exist
        logger.exception("DSB User Personal document with ID %s does not exist", document_id)
        raise
    except Document.DoesNotExist:
        # Log the error information if the document associated with the DSB User Personal instance does not exist
        logger.exception("Document associated with DSB User Personal ID %s does not exist", document_id)
        raise
    except User.DoesNotExist:
        # Log the error information if the user does not exist
        logger.exception("User with ID %s does not exist", user_id)
        raise
    except Exception as e:
        # Log the error information
        logger.exception("Error processing document %s: %s", document_id, str(e))  # noqa: TRY401
        raise
