from __future__ import annotations

import logging
import pathlib
from typing import Any

from celery import chain, group, shared_task  #type: ignore  # noqa: PGH003

from app.documents.dttotDoc.dttotDocReport.tasks import (  #type: ignore  # noqa: PGH003
    create_or_update_dttotdoc_report,
    update_dttotdoc_report_score,
)
from app.documents.dttotDoc.dttotDocReportCorporate.tasks import (  #type: ignore  # noqa: PGH003
    scoring_similarity_corporate,
)
from app.documents.dttotDoc.dttotDocReportPersonal.tasks import (  #type: ignore  # noqa: PGH003
    scoring_similarity_personal,
)
from app.documents.dttotDoc.dttotDocReportPublisher.tasks import (  #type: ignore  # noqa: PGH003
    scoring_similarity_publisher,
)
from app.documents.dttotDoc.utils import (
    handle_dttot_document,  #type: ignore  # noqa: PGH003
)
from app.documents.models import Document  #type: ignore  # noqa: PGH003
from app.documents.utils.data_preparation import (  #type: ignore  # noqa: PGH003
    CleaningSeparatingDeskripsi,
    DTTOTDocumentProcessing,
    ExtractNIKandPassportNumber,
    FormattingColumn,
)
from app.dsb_user.dsb_user_corporate.tasks import (  #type: ignore  # noqa: PGH003
    process_dsb_user_corporate_document,
)
from app.dsb_user.dsb_user_personal.tasks import (  #type: ignore  # noqa: PGH003
    process_dsb_user_personal_document,
)
from app.dsb_user.dsb_user_publisher.tasks import (  #type: ignore  # noqa: PGH003
    process_dsb_user_publisher_document,
)
from app.user.models import User  #type: ignore  # noqa: PGH003

logger = logging.getLogger(__name__)

@shared_task()
def process_dttot_document_row(
    row_data: dict[str, Any],
    user_id: str,
    document_id: str,
) -> None:
    try:
        # Retrieve the Document instance
        document = Document.objects.get(pk=document_id)
        dttot_id = handle_dttot_document(
            document=document,
            row_data=row_data,
            user_data=user_id,
        )
        logger.info(
            "Successfully processed row for document ID %s, dttot ID %s",
            document_id, dttot_id,
        )
    except Exception:
        logger.exception("Error processing row for document ID %s", document_id)
        raise

@shared_task()
def process_dttot_document(
    user_id: str,
    document_id: str,
) -> None:
    try:
        # Retrieve the Document instance
        document = Document.objects.get(pk=document_id)

        # Retrieve the User instance
        user = User.objects.get(pk=user_id)

        # Verify that the document has a file
        if not document.document_file or not document.document_file.path:
            msg = "The document_file attribute is not set or has no associated file"
            raise ValueError(msg)  # noqa: TRY301

        # Perform all steps in sequence to ensure no overlap
        processor = DTTOTDocumentProcessing()
        data_frame = processor.retrieve_data_as_dataframe(
            document.document_file.path,
            document.document_file_type.upper(),
        )
        data_frame = processor.extract_and_split_names(data_frame, "Nama", case_insensitive=False)
        cleaner = CleaningSeparatingDeskripsi()
        data_frame = cleaner.separating_cleaning_deskripsi(data_frame)
        extractor = ExtractNIKandPassportNumber()
        data_frame = extractor.extract_nik_and_passport_number(data_frame)
        formatter = FormattingColumn()
        data_frame = formatter.format_birth_date(data_frame)
        data_frame = formatter.format_nationality(data_frame)

        # Dispatch tasks to process each row
        tasks = [
            process_dttot_document_row.s(
                document_id=document.pk,
                row_data=row.to_dict(),
                user_id=user.pk,
            )
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

@shared_task()
def initiate_document_processing(
    user_data_serializable: str,
    document_data_serializable: str,
) -> None:
    """To initiate the document processing sequence.

    This function creates a Celery task chain that consists of the following steps:

    1. Check if the Document is created.
    2. Process the DTTOT document.
    3. Process the DSB User Personal document.
    4. Create a new DTTOT Document Report.
    5. Score the similarity between the DTTOT document and the DTTOT Doc Report.
    6. Update the DTTOT Document Report score.

    Args:
    ----
        user_data_serializable (str): The serialized user data.
        document_data_serializable (str): The serialized document data.
        report_path (pathlib.Path): The directory path of report that will be generated

    Returns:
    -------
        None

    """
    # Create a chain of tasks
    task_chain = chain(
        process_dttot_document.si(user_data_serializable, document_data_serializable),
        process_dsb_user_personal_document.si(user_data_serializable, document_data_serializable),
        process_dsb_user_publisher_document.si(user_data_serializable, document_data_serializable),
        process_dsb_user_corporate_document.si(user_data_serializable, document_data_serializable),
        create_or_update_dttotdoc_report.si(document_data_serializable),
        scoring_similarity_personal.si(document_data_serializable),
        scoring_similarity_corporate.si(document_data_serializable),
        scoring_similarity_publisher.si(document_data_serializable),
        update_dttotdoc_report_score.si(document_data_serializable))()
