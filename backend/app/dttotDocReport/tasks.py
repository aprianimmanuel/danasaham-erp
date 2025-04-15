from __future__ import annotations

import logging

from celery import shared_task  #type: ignore # noqa: PGH003

from app.documents.models import Document  #type: ignore # noqa: PGH003
from app.dttotDocReport.models import dttotDocReport  #type: ignore # noqa: PGH003
from app.dttotDocReport.serializers import (  #type: ignore # noqa: PGH003
    dttotDocReportSerializer,
)
from app.dttotDocReportPersonal.models import (  #type: ignore # noqa: PGH003
    dttotDocReportPersonal,
)

MATCH_SIMILARITY_THRESHOLD = 0.8

logger = logging.getLogger(__name__)


@shared_task(acks_late=True)
def create_or_update_dttotdoc_report(document_id: str) -> str:
    """Create or update an entry in dttotDocReport and return its ID.

    This task checks if a dttotDocReport exists for the given document ID.
    If it exists, the task updates the entry. Otherwise, it creates a new one.

    Args:
    ----
        document_id (str): The ID of the document to create or update the dttotDocReport for.

    Returns:
    -------
        str: The ID of the created or updated dttotDocReport.

    Raises:
    ------
        ValueError: If the document ID is not provided or if the operation fails.

    """
    # Log the start of the task
    logger.info("Starting task to create or update dttotDocReport for document_id=%s", document_id)

    try:
        # Get document instance
        document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        msg = f"Document with ID {document_id} does not exist."
        logger.exception(msg)
        raise ValueError(msg)  # noqa: B904

    # Prepare data for the serializer
    dttotdoc_report_data = {
        "document": document.document_id,
        "status_doc": "Initialized",
    }

    try:
        # Check if a dttotDocReport already exists for this document
        dttotdoc_report = dttotDocReport.objects.get(document=document)
        serializer = dttotDocReportSerializer(dttotdoc_report, data=dttotdoc_report_data, partial=True)
    except dttotDocReport.DoesNotExist:
        # If not, create a new one
        serializer = dttotDocReportSerializer(data=dttotdoc_report_data)

    if serializer.is_valid():
        dttotdoc_report = serializer.save()
        logger.info("Successfully created or updated dttotDocReport: %s", dttotdoc_report.dttotdoc_report_id)
        return dttotdoc_report.dttotdoc_report_id
    else:  # noqa: RET505
        msg = "Failed to create or update dttotDocReport: %s"
        logger.error(msg, serializer.errors)
        raise ValueError(msg, serializer.errors)

@shared_task()
def update_dttotdoc_report_score(
    document_id: str,
) -> None:
    """Update the DTTOT Doc Report status based on the associated personal similarity scores.

    This task checks the associated `dttotDocReportPersonal` records for the given document.
    If valid similarity scores are found, it updates the `status_doc` to "DONE". Otherwise, it sets it to "FAILED".

    Args:
    ----
        document_id (str): The ID of the document to update the DTTOT Doc Report for.

    Returns:
    -------
        None

    Raises:
    ------
        dttotDocReport.DoesNotExist: If the DTTOT Doc Report instance does not exist.
        Exception: For any other errors during execution.

    """
    # Log the start of the task
    logger.info("Starting task to update dttotDocReport status for document_id=%s", document_id)

    try:
        # Retrieve the DTTOT Doc Report
        dttot_report = dttotDocReport.objects.get(document=document_id)
        dttot_doc_report_id = dttot_report.dttotdoc_report_id

        # Retrieve associated personal records and check for valid similarity scores
        dttot_report_personals = dttotDocReportPersonal.objects.filter(dttotdoc_report=dttot_doc_report_id)
        valid_scores_exist = dttot_report_personals.filter(score_match_similarity__gte=MATCH_SIMILARITY_THRESHOLD).exists()

        # Update the status based on the presence of valid scores
        if valid_scores_exist:
            dttot_report.status_doc = "DONE"
            logger.info("Updated dttotDocReport ID=%s with status_doc=%s", dttot_doc_report_id, dttot_report.status_doc)
        else:
            dttot_report.status_doc = "SUCCESS"
            logger.warning("No valid similarity scores found. Updated dttotDocReport ID=%s with status_doc=%s", dttot_doc_report_id, dttot_report.status_doc)

        dttot_report.save()

    except dttotDocReport.DoesNotExist:
        msg = "dttotDocReport with ID %s not found"
        logger.exception(msg, document_id)
        raise
    except Exception as e:
        logger.exception("Error updating DTTOT Doc Report for document_id=%s", document_id)
        raise
