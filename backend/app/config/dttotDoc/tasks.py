import logging
from app.config.documents.utils.data_preparation import (
    DTTOTDocumentProcessing,
    ExtractNIKandPassportNumber,
    CleaningSeparatingDeskripsi,
    FormattingColumn
)
from app.config.dttotDoc.utils import handle_dttot_document
from app.config.core.models import Document, User
from celery import shared_task, group


logger = logging.getLogger(__name__)

@shared_task
def process_dttot_document_row(document_id, row_data, user_id):
    try:
        document = Document.objects.get(pk=document_id)
        handle_dttot_document(document, row_data, user_id)
        logger.info(f"Successfully processed row for document ID {document_id}")
    except Exception as e:
        logger.error(f"Error processing row for document ID {document_id}: {e}")
        raise


@shared_task
def process_dttot_document(document_id):
    try:
        document = Document.objects.get(pk=document_id)
        user_id = document.created_by_id

        # Perform all steps in sequence to ensure no overlap
        df = DTTOTDocumentProcessing().retrieve_data_as_dataframe(document.document_file.path, document.document_file_type.upper())
        df = ExtractNIKandPassportNumber().extract_nik_and_passport_number(df)
        df = CleaningSeparatingDeskripsi().separating_cleaning_deskripsi(df)
        df = FormattingColumn().format_birth_date(df)
        df = FormattingColumn().format_nationality(df)

        # Dispatch tasks to process each row
        tasks = [process_dttot_document_row.s(document_id, row.to_dict(), user_id) for _, row in df.iterrows()]
        group(tasks).apply_async()
        logger.info(f"Successfully dispatched row processing tasks for document ID {document_id}")
    except Exception as e:
        logger.error(f"Error processing document ID {document_id}: {e}")
        raise