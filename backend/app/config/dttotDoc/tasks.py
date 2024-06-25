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
import copy

logger = logging.getLogger(__name__)

@shared_task
def process_dttot_document_row(document_id, row_data, user_id):
    try:
        row_data_copy = copy.deepcopy(row_data)
        document = Document.objects.get(pk=document_id)
        dttot_id = handle_dttot_document(document, row_data_copy, user_id)
        logger.info(f"Successfully processed row for document ID {document_id}, dttot ID {dttot_id}")
    except Exception as e:
        logger.error(f"Error processing row for document ID {document_id}: {e}")
        raise


@shared_task
def process_dttot_document(document_id, user_data):
    try:
        user_data_copy = copy.deepcopy(user_data)
        document = Document.objects.get(pk=document_id)
        user_id = user_data_copy['user_id']

        if not document.document_file or not document.document_file.path:
            raise ValueError("The document_file attribute is not set or has no associated file")

        # Perform all steps in sequence to ensure no overlap
        processor = DTTOTDocumentProcessing()
        df = processor.retrieve_data_as_dataframe(document.document_file.path, document.document_file_type.upper())
        df = processor.extract_and_split_names(df, 'Nama')
        cleaner = CleaningSeparatingDeskripsi()
        df = cleaner.separating_cleaning_deskripsi(df)
        extractor = ExtractNIKandPassportNumber()
        df = extractor.extract_nik_and_passport_number(df)
        formatter = FormattingColumn()
        df = formatter.format_birth_date(df)
        df = formatter.format_nationality(df)

        # Dispatch tasks to process each row
        tasks = [process_dttot_document_row.s(document_id, row.to_dict(), user_id) for _, row in df.iterrows()]
        group(tasks).apply_async()
        logger.info(f"Successfully dispatched row processing tasks for document ID {document_id}")
    except Exception as e:
        logger.error(f"Error processing document ID {document_id}: {e}")
        raise