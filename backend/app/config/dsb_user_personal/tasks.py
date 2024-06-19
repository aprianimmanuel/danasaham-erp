from celery import shared_task, group
from app.config.dsb_user_personal.utils.utils import fetch_data_from_external_db, save_data_to_model
from app.config.core.models import Document
import logging

logger = logging.getLogger(__name__)

@shared_task
def process_dsb_user_personal_document(document_id, user_data):
    try:
        document = Document.objects.get(pk=document_id)
        user = user_data['user_id']

        df = fetch_data_from_external_db()
        tasks = [save_data_to_model_row.s(row.to_dict(), document, user) for _, row in df.iterrows()]
        group(tasks).apply_async()

        document.status = 'Processing'
        document.save()
        logger.info(f"Document {document_id} is being processed.")
    except Exception as e:
        document.status = 'Failed'
        document.save()
        logger.error(f"Error processing document {document_id}: {e}")
        raise e

@shared_task
def save_data_to_model_row(row_data, document, user_id):
    try:
        save_data_to_model(row_data, document, user_id)
    except Exception as e:
        logger.error(f"Error saving row data for document {document.document_id}: {e}")
        raise e