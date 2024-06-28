from __future__ import annotations

import logging

from celery import shared_task

from app.config.core.models import Document
from app.config.dsb_user_personal.utils.utils import (
    fetch_data_from_external_db,
    save_data_to_model,
)

logger = logging.getLogger(__name__)


@shared_task
def process_dsb_user_personal_document(document_id, user_data) -> None:
    try:
        document = Document.objects.get(pk=document_id)
        user_id = user_data["user_id"]

        df = fetch_data_from_external_db()
        save_data_to_model(df, document, user_id)

        document.status = "Processed"
        document.save()
        logger.info(f"Document {document_id} is being processed.")
    except Exception as e:
        document.status = "Failed"
        document.save()
        logger.exception(f"Error processing document {document_id}: {e}")
        raise
