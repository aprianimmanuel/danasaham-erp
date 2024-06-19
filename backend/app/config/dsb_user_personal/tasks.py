from celery import shared_task
from app.config.dsb_user_personal.utils.utils import fetch_data_from_external_db, save_data_to_model
from app.config.core.models import Document

@shared_task
def process_dsb_user_personal_document(document_id):
    try:
        document = Document.objects.get(pk=document_id)
        df = fetch_data_from_external_db()
        save_data_to_model(df)
        document.status = 'Processed'
        document.save()
    except Exception as e:
        document.status = 'Failed'
        document.save()
        raise e