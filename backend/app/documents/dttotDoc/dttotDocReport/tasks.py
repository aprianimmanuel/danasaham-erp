from __future__ import annotations

import logging

from celery import shared_task  #type: ignore # noqa: PGH003

from app.documents.dttotDoc.dttotDocReport.models import (
    DttotDocReport,  #type: ignore # noqa: PGH003
)
from app.documents.dttotDoc.dttotDocReport.serializers import (  #type: ignore # noqa: PGH003
    dttotDocReportSerializer,
)
from app.documents.dttotDoc.dttotDocReportCorporate.models import DttotDocReportCorporate
from app.documents.dttotDoc.dttotDocReportPersonal.models import (  #type: ignore # noqa: PGH003
    DttotDocReportPersonal,
)
from app.documents.dttotDoc.dttotDocReportPublisher.models import DttotDocReportPublisher
from app.documents.models import Document  #type: ignore # noqa: PGH003

MATCH_SIMILARITY_THRESHOLD = 0.8

logger = logging.getLogger(__name__)


@shared_task(acks_late=True)
def create_or_update_dttotdoc_report(
    document_id: str,
) -> str:
    """Create or update an entry in dttotDocReport and return its ID.

    This task checks if a dttotDocReport exists for the given document ID.
    If it exists, the task updates the entry. Otherwise, it creates a new one.

    Args:
    ----
        document_id (str): The ID of the document to create or update the dttotDocReport for.
        report_path (pathlib.Path): The path to the report file.

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
        dttotdoc_report = DttotDocReport.objects.get(document=document)
        serializer = dttotDocReportSerializer(
            dttotdoc_report,
            data=dttotdoc_report_data,
            partial=True,
        )
    except DttotDocReport.DoesNotExist:
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
def update_dttotdoc_report_score(document_id: str) -> None:
    """Update DTTOT Doc Report status based on associated similarity scores.

    Args:
        document_id (str): The ID of the document to update.

    Returns:
        None

    Raises:
        DttotDocReport.DoesNotExist: If the DTTOT Doc Report instance does not exist.
        Exception: For any other errors during execution.

    """
    logger.info("Starting task to update DTTOT Doc Report status for document_id=%s", document_id)

    try:
        # Retrieve the DTTOT Doc Report
        dttot_report = DttotDocReport.objects.get(document=document_id)
        dttot_doc_report_id = dttot_report.dttotdoc_report_id

        # Retrieve associated records
        dttot_report_personals = DttotDocReportPersonal.objects.filter(dttotdoc_report__in=dttot_doc_report_id)
        dttot_report_publishers = DttotDocReportPublisher.objects.filter(dttodoc_report__in=dttot_doc_report_id)
        dttot_report_corporates = DttotDocReportCorporate.objects.filter(dttotdoc_report__in=dttot_doc_report_id)

        # Check for valid similarity scores
        valid_scores_exist = (
            dttot_report_personals.filter(score_match_similarity__gte=MATCH_SIMILARITY_THRESHOLD).exists() or
            dttot_report_publishers.filter(score_match_similarity__gte=MATCH_SIMILARITY_THRESHOLD).exists() or
            dttot_report_corporates.filter(score_match_similarity__gte=MATCH_SIMILARITY_THRESHOLD).exists()
        )

        # Update the status based on valid scores
        dttot_report.status_doc = "DONE" if valid_scores_exist else "FAILED"
        logger.info("Updated DTTOT Doc Report ID=%s with status_doc=%s", dttot_doc_report_id, dttot_report.status_doc)

        # Save changes
        dttot_report.save()

    except DttotDocReport.DoesNotExist:
        logger.exception("DTTOT Doc Report with document_id=%s not found", document_id)
        raise
    except Exception as e:
        logger.exception("Error updating DTTOT Doc Report for document_id=%s: %s", document_id, str(e))
        raise
