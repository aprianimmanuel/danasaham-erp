from __future__ import annotations

import logging
from datetime import date

from celery import shared_task

from app.config.core.models import (
    dsb_user_personal,
    dttotDoc,
    dttotDocReport,
)
from app.config.dttotDocReportPersonal.utils.utils import (
    save_report_data_row_by_row,
)

logger = logging.getLogger(__name__)

KODE_DENSUS_THRESHOLD = 0.8

@shared_task()
def scoring_similarity_personal(
    document_id: str,
) -> str:
    """Processes a DTTOT Doc Report Personal.

    This task retrieves the DTTOT Doc and DSB User Personal data and calculates the similarity scores
    between the two. It then creates or updates a DTTOT Doc Report Personal entry with the calculated
    similarity scores and kode_densus_personal.

    Args:
    ----
       document_id (str): The ID of the DTTOT Doc Report to process.

    Returns:
    -------
        str: The ID of the created or updated dttotDocReportPersonal.

    """  # noqa: D401
    # Log the start of the task
    logger.info("Processing DTTOT Doc Report Personal for document ID: %s", document_id)

    try:
        # Get dttotDocReport instance
        dttot_doc_report = dttotDocReport.objects.get(document=document_id)

        # Retrieve the DTTOT Docs associated with the document_id
        dttot_docs = dttotDoc.objects.filter(document=document_id)

        # Retrieve the DSB User Personals associated with the document_id
        dsb_user_personals = dsb_user_personal.objects.filter(document=document_id)

        # Check if the document ID is provided
        if not dttot_docs.exists() or not dsb_user_personals.exists():
            msg = "DTTOT Doc or DSB User Personal data not found for document ID: %s", document_id
            logger.error(msg)
            raise ValueError(msg)  # noqa: TRY301

        total_iterations = len(dttot_docs) * len(dsb_user_personals)
        current_iteration = 0

        # Iterate over each dttotDoc and compare with each DSB User Personal
        for dttot_doc in dttot_docs:
            for dsb_user in dsb_user_personals:
                current_iteration += 1
                progress = (current_iteration / total_iterations) * 100
                logger.info(
                    "Processing iteration %d/%d (%.2f%%) for DTTOT Doc ID: %s and DSB User Personal ID: %s",
                    current_iteration,
                    total_iterations,
                    progress,
                    dttot_doc.dttot_id,
                    dsb_user.dsb_user_personal_id,
                )

                # Prepare the personal data
                personal_data = {
                    "personal_nik": dsb_user.personal_nik,
                    "user_name": dsb_user.user_name,
                    "personal_phone_number": dsb_user.personal_phone_number,
                    "personal_spouse_name": dsb_user.personal_spouse_name,
                    "personal_mother_name": dsb_user.personal_mother_name,
                    "personal_domicile_address": dsb_user.personal_domicile_address,
                    "personal_birth_date": dsb_user.personal_birth_date.strftime("%Y-%m-%d") if isinstance(dsb_user.personal_birth_date, date) else dsb_user.personal_birth_date,
                    "personal_birth_place": dsb_user.personal_birth_place,
                    "personal_nationality": dsb_user.personal_nationality,
                    "personal_description": " ".join(filter(None, [
                        dsb_user.personal_nik,
                        dsb_user.user_name,
                        dsb_user.personal_phone_number,
                        dsb_user.personal_spouse_name,
                        dsb_user.personal_mother_name,
                        dsb_user.personal_domicile_address,
                        dsb_user.personal_birth_date.strftime("%Y-%m-%d") if isinstance(dsb_user.personal_birth_date, date) else dsb_user.personal_birth_date,
                        dsb_user.personal_birth_place,
                        dsb_user.personal_nationality,
                    ])),
                }

                # Save the report data row by row
                save_report_data_row_by_row(
                    dttot_doc_report,
                    dsb_user.dsb_user_personal_id,
                    personal_data,
                    dttot_doc,
                )
                logger.info(
                    "Successfully processed and updated report for DTTOT Doc ID: %s and DSB User Personal ID: %s",
                    dttot_doc.dttot_id,
                    dsb_user.pk,
                )

        return "Successfully processed all records."  # noqa: TRY300

    except Exception as e:
        logger.exception("Error processing DTTOT Doc Report Personal: %s", str(e))  # noqa: TRY401
        raise
