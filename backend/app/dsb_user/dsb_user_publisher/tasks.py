from __future__ import annotations

import logging

from celery import shared_task  #type: ignore # noqa: PGH003

from app.documents.models import Document  #type: ignore # noqa: PGH003
from app.dsb_user.dsb_user_publisher.models import (  #type: ignore # noqa: PGH003
    DsbUserPublisher,
)
from app.dsb_user.dsb_user_publisher.utils.utils import (  #type: ignore # noqa: PGH003
    fetch_data_from_external_db,
    save_data_to_model,
)
from app.user.models import User  #type: ignore # noqa: PGH003

logger = logging.getLogger(__name__)


@shared_task()
def process_dsb_user_publisher_document(
    user_id: str,
    document_id: str,
) -> None:
    """Process DSB User Publisher document.

    This function fetches data from the external database, saves it to the model,
    and updates the document status.

    Args:
    ----
        document_id (str): The ID of the document to process.
        user_id (str): The ID of the user to process.

    Raises:
    ------
        Document.DoesNotExist: If the document associated with the DSB User Publisher instance does not exist.
        User.DoesNotExist: If the user does not exist.

    """
    try:
        # Get the document and user objects
        document_process_dsb_publisher_document = Document.objects.get(pk=document_id)
        user_process_dsb_user_publisher_document = User.objects.get(pk=user_id)

        # Retrieve the Document instance
        if not document_process_dsb_publisher_document:
            msg = "Document ID not found in context"
            raise ValueError(msg)

        # Retrieve the User instance
        if not user_process_dsb_user_publisher_document:
            msg = "User ID not found in context"
            raise ValueError(msg)

        # Fetch data from the external database
        df = fetch_data_from_external_db()  # noqa: PD901

        # Save data to the model
        save_data_to_model(df, document_process_dsb_publisher_document, user_process_dsb_user_publisher_document)

        # Log the processing information
        logger.info("Document %s is being processed.", DsbUserPublisher.pk)

    except DsbUserPublisher.DoesNotExist:
        # Log the error information
        logger.exception("Error processing document %s", DsbUserPublisher.pk)
        raise
    except Document.DoesNotExist:
        # Log the error information
        logger.exception("Document %s does not exist.", DsbUserPublisher.pk)
        raise
    except User.DoesNotExist:
        # Log the error information
        logger.exception("User %s does not exist.", DsbUserPublisher.pk)
        raise
