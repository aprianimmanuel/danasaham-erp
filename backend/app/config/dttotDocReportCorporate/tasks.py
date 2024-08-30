from __future__ import annotations

import logging
from datetime import date

from celery import shared_task

from app.config.core.models import (
    dsb_user_corporate,
    dttotDoc,
    dttotDocReport,
)
from app.config.dttotDocReportCorporate.utils.utils import (
    save_report_data_row_by_row,
)

logger = logging.getLogger(__name__)

SIMILARITY_THRESOLD = 0.9

@shared_task()
def scoring_similarity_corporate(
    document_id: str,
) -> str:
    """To process a DTTOT Doc Report Corporate.

    This task retrieves the DTTOT Doc and DSB User Corporate data and calculates the similarity scores
    between the two. It then creates or updates a DTTOT Doc Report Corporate entry with the calculated
    similarity scores and kode_densus_corporate.

    Args:
    ----
       document_id (str): The ID of the DTTOT Doc Report to process.

    Returns:
    -------
        str: The ID of the created or updated dttotDocReportCorporate.

    """
    # Log the start of the task
    logger.info("Processing DTTOT Doc Report Corporate for document ID: %s", document_id)

    try:
        # Get dttotDocReport instance
        dttot_doc_report = dttotDocReport.objects.get(document=document_id)

        # Retrieve the DTTOT Docs associated with the document_id
        dttot_docs = dttotDoc.objects.filter(document=document_id)

        # Retrieve the DSB User Corporates associated with the document_id
        dsb_user_corps = dsb_user_corporate.objects.filter(
            document=document_id,
        )

        # Check if the document ID is provided
        if not dttot_docs.exists() or not dsb_user_corps.exists():
            msg = "DTTOT Doc or DSB User Corporate data not found for document ID: %s", document_id
            logger.error(msg)
            raise ValueError(msg)  # noqa: TRY301

        total_iterations = len(dttot_docs) * len(dsb_user_corps)
        current_iteration = 0

        for dttot_doc in dttot_docs:
            for dsb_user_corp in dsb_user_corps:
                current_iteration += 1
                progress = (current_iteration / total_iterations) * 100
                logger.info(
                    "Processing iteration %d/%d (%.2f%%) for DTTOT Doc ID: %s and DSB User Corporate ID: %s",
                    current_iteration,
                    total_iterations,
                    progress,
                    dttot_doc.dttot_id,
                    dsb_user_corp.dsb_user_corporate_id,
                )

                # Prepare the corporate data
                corporate_data = {
                    "corporate_company_name": dsb_user_corp.corporate_company_name,
                    "corporate_phone_number": dsb_user_corp.corporate_phone_number,
                    "corporate_nib": dsb_user_corp.corporate_nib,
                    "corporate_npwp": dsb_user_corp.corporate_npwp,
                    "corporate_siup": dsb_user_corp.corporate_siup,
                    "corporate_skdp": dsb_user_corp.corporate_skdp,
                    "corporate_domicile_address": dsb_user_corp.corporate_domicile_address,
                    "corporate_user_name": dsb_user_corp.user_name,
                    "corporate_user_phone_number": dsb_user_corp.users_phone_number,
                    "corporate_description_scores": " ".join(
                        filter(None, [
                            dsb_user_corp.corporate_company_name,
                            dsb_user_corp.corporate_phone_number,
                            dsb_user_corp.corporate_nib,
                            dsb_user_corp.corporate_npwp,
                            dsb_user_corp.corporate_siup,
                            dsb_user_corp.corporate_skdp,
                            dsb_user_corp.corporate_domicile_address,
                            dsb_user_corp.user_name,
                            dsb_user_corp.users_phone_number,
                        ]),
                    ),
                    "pengurus_corporate_name": dsb_user_corp.pengurus_corporate_name,
                    "pengurus_corporate_phone_number": dsb_user_corp.pengurus_corporate_phone_number,
                    "pengurus_corporate_id_number": dsb_user_corp.pengurus_corporate_id_number,
                    "pengurus_corporate_place_of_birth": dsb_user_corp.pengurus_corporate_place_of_birth,
                    "pengurus_corporate_date_of_birth": dsb_user_corp.pengurus_corporate_date_of_birth.strftime("%Y-%m-%d") if isinstance(dsb_user_corp.pengurus_corporate_date_of_birth, date) else dsb_user_corp.pengurus_corporate_date_of_birth,
                    "pengurus_corporate_domicile_Address": dsb_user_corp.pengurus_corporate_domicile_address,
                    "pengurus_corporate_description": " ".join(
                        filter(None, [
                            dsb_user_corp.pengurus_corporate_name,
                            dsb_user_corp.pengurus_corporate_phone_number,
                            dsb_user_corp.pengurus_corporate_id_number,
                            dsb_user_corp.pengurus_corporate_place_of_birth,
                            dsb_user_corp.pengurus_corporate_date_of_birth.strftime("%Y-%m-%d") if isinstance(dsb_user_corp.pengurus_corporate_date_of_birth, date) else dsb_user_corp.pengurus_corporate_date_of_birth,
                            dsb_user_corp.pengurus_corporate_domicile_address,
                        ],
                    ),
                ),
            }

                # Save the corporate data
                save_report_data_row_by_row(
                    dttot_doc_report,
                    dsb_user_corp.dsb_user_corporate_id,
                    corporate_data,
                    dttot_doc,
                )
                logger.info(
                    "Processed iteration %d/%d (%.2f%%) for DTTOT Doc ID: %s and DSB User Corporate ID: %s",
                    current_iteration,
                    total_iterations,
                    progress,
                    dttot_doc.dttot_id,
                    dsb_user_corp.dsb_user_corporate_id,
                )

        return "Successfulyy processed all records."  # noqa: TRY300

    except Exception:
        logger.exception("Error processing document ID %s", document_id)
        raise
