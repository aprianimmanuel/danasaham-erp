from __future__ import annotations

import copy
import logging
from typing import Any

from celery import group, shared_task

from app.config.core.models import Document
from app.config.documents.utils.data_preparation import (
    CleaningSeparatingDeskripsi,
    DTTOTDocumentProcessing,
    ExtractNIKandPassportNumber,
    FormattingColumn,
)
from app.config.dttotDoc.utils import handle_dttot_document

logger = logging.getLogger(__name__)

@shared_task
def process_dttot_document_row(document_id: int, row_data: dict[str, Any], user_id: int) -> None:
    try:
        row_data_copy = copy.deepcopy(row_data)
        document = Document.objects.get(pk=document_id)
        dttot_id = handle_dttot_document(document, row_data_copy, user_id)
        logger.info(
            "Successfully processed row for document ID %s, dttot ID %s",
            document_id, dttot_id,
        )
    except Exception:
        logger.exception("Error processing row for document ID %s", document_id)
        raise

@shared_task
def process_dttot_document(document_id: int, user_data: dict[str, Any]) -> None:
    def raise_value_error(msg: str) -> None:
        raise ValueError(msg)

    try:
        user_data_copy = copy.deepcopy(user_data)
        document = Document.objects.get(pk=document_id)
        user_id = user_data_copy["user_id"]

        if not document.document_file or not document.document_file.path:
            raise_value_error("The document_file attribute is not set or has no associated file")

        # Perform all steps in sequence to ensure no overlap
        processor = DTTOTDocumentProcessing()
        data_frame = processor.retrieve_data_as_dataframe(
            document.document_file.path,
            document.document_file_type.upper(),
        )
        data_frame = processor.extract_and_split_names(data_frame, "Nama")
        cleaner = CleaningSeparatingDeskripsi()
        data_frame = cleaner.separating_cleaning_deskripsi(data_frame)
        extractor = ExtractNIKandPassportNumber()
        data_frame = extractor.extract_nik_and_passport_number(data_frame)
        formatter = FormattingColumn()
        data_frame = formatter.format_birth_date(data_frame)
        data_frame = formatter.format_nationality(data_frame)

        # Dispatch tasks to process each row
        tasks = [
            process_dttot_document_row.s(document_id, row.to_dict(), user_id)
            for _, row in data_frame.iterrows()
        ]
        group(tasks).apply_async()
        logger.info(
            "Successfully dispatched row processing tasks for document ID %s",
            document_id,
        )
    except Exception:
        logger.exception("Error processing document ID %s", document_id)
        raise
