from __future__ import annotations

import logging
from datetime import date

from celery import shared_task

from app.config.core.models import (
    dsb_user_publisher,
    dttotDoc,
    dttotDocReport,
)
from app.config.dttotDocReportPublisher.utils.utils import (
    save_report_data_row_by_row,
)

logger = logging.getLogger(__name__)

KODE_DENSUS_THRESHOLD = 0.8


@shared_task()
def scoring_similarity_publisher(
    document_id: str,
) -> str:
    """To process a DTTOT Doc Report Publisher.

    This task retrieves the DTTOT Doc and DSB User Publisher data and calculates the similarity scores
    between the two. It then creates or updates a DTTOT Doc Report Publisher entry with the calculated
    similarity scores and kode_densus_publisher.

    Args:
    ----
       document_id (str): The ID of the DTTOT Doc Report to process.

    Returns:
    -------
        str: The ID of the created or updated dttotDocReportPublisher.

    """
    # Log the start of the task
    logger.info("Processing DTTOT Doc Report Publisher for document ID: %s", document_id)

    try:
        # Get dttotDocReport instance
        dttot_doc_report = dttotDocReport.objects.get(document=document_id)

        # Retrieve the DTTOT Docs associated with the document_id
        dttot_docs = dttotDoc.objects.filter(document=document_id)

        # Retrieve the DSB User Publishers associated with the document_id
        dsb_user_pubs = dsb_user_publisher.objects.filter(
            document=document_id,
        )

        # Check if the document ID is provided
        if not dttot_docs.exists() or not dsb_user_pubs.exists():
            msg = "DTTOT Doc or DSB User Publisher data not found for document ID: %s", document_id
            logger.error(msg)
            raise ValueError(msg)  # noqa: TRY301

        total_iterations = len(dttot_docs) * len(dsb_user_pubs)
        current_iteration = 0

        for dttot_doc in dttot_docs:
            for dsb_user_pub in dsb_user_pubs:
                current_iteration += 1
                progress = (current_iteration / total_iterations) * 100
                logger.info(
                    "Processing iteration %d/%d (%.2f%%) for DTTOT Doc ID: %s and DSB User Publisher ID: %s",
                    current_iteration,
                    total_iterations,
                    progress,
                    dttot_doc.dttot_id,
                    dsb_user_pub.dsb_user_publisher_id,
                )

                # Prepare the publisher data
                publisher_data = {
                    "publisher_registered_name": dsb_user_pub.publisher_registered_name,
                    "publisher_phone_number": dsb_user_pub.publisher_phone_number,
                    "domicile_address_publisher_1": dsb_user_pub.domicile_address_publisher_1,
                    "domicile_address_publisher_2": dsb_user_pub.domicile_address_publisher_2,
                    "domicile_address_publisher_3_city": dsb_user_pub.domicile_address_publisher_3_city,
                    "publisher_description": " ".join(filter(None, [
                        dsb_user_pub.publisher_registered_name,
                        dsb_user_pub.publisher_phone_number,
                        dsb_user_pub.domicile_address_publisher_1,
                        dsb_user_pub.domicile_address_publisher_2,
                        dsb_user_pub.domicile_address_publisher_3_city,
                    ])),
                    "publisher_pengurus_names": dsb_user_pub.publisher_pengurus_name,
                    "publisher_pengurus_id_number": dsb_user_pub.publisher_pengurus_id_number,
                    "publisher_pengurus_phone_number": dsb_user_pub.publisher_pengurus_phone_number,
                    "publisher_address_pengurus": dsb_user_pub.publisher_address_pengurus,
                    "publisher_tgl_lahir_pengurus": dsb_user_pub.publisher_tgl_lahir_pengurus.strftime("%Y-%m-%d") if isinstance(dsb_user_pub.publisher_tgl_lahir_pengurus, date) else dsb_user_pub.publisher_tgl_lahir_pengurus,
                    "publisher_tempat_lahir_pengurus": dsb_user_pub.publisher_tempat_lahir_pengurus,
                    "pengurus_publisher_description": " ".join(
                        filter(
                            None, [
                                dsb_user_pub.publisher_pengurus_name,
                                dsb_user_pub.publisher_pengurus_id_number,
                                dsb_user_pub.publisher_pengurus_phone_number,
                                dsb_user_pub.publisher_address_pengurus,
                                dsb_user_pub.publisher_tgl_lahir_pengurus.strftime("%Y-%m-%d") if isinstance(dsb_user_pub.publisher_tgl_lahir_pengurus, date) else dsb_user_pub.publisher_tgl_lahir_pengurus,
                                dsb_user_pub.publisher_tempat_lahir_pengurus,
                            ],
                        ),
                    ),
                }

                # Save the publisher data
                save_report_data_row_by_row(
                    dttot_doc_report,
                    dsb_user_pub.dsb_user_publisher_id,
                    publisher_data,
                    dttot_doc,
                )
                logger.info(
                    "Successfully processed and updated report for DTTOT Doc ID: %s and DSB User Publisher ID: %s",
                    dttot_doc.dttot_id,
                    dsb_user_pub.pk,
                )

        return "Successfully processed all records."  # noqa: TRY300

    except Exception as e:
        logger.exception("Error processing DTTOT Doc Report Publisher: %s", str(e))  # noqa: TRY401
        raise
