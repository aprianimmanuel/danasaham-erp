from __future__ import annotations

import difflib
import logging
from typing import Any

from rest_framework.exceptions import ValidationError

from app.config.core.models import dttotDoc
from app.config.dttotDoc.serializers import DttotDocSerializer

logger = logging.getLogger(__name__)

MAGIC_COMPARISON_RATIO: float = 0.90

def handle_dttot_document(document: Any, row_data: dict[str, Any], user_id: int) -> int:
    try:
        existing_kode_densus = set(
            dttotDoc.objects.values_list("dttot_kode_densus", flat=True),
        )
        kode_densus = row_data.get("Kode Densus", "")
        if not any(
            difflib.SequenceMatcher(None, kode_densus, existing).ratio() > MAGIC_COMPARISON_RATIO
            for existing in existing_kode_densus
        ):
            row_data.update(
                {
                    "user": user_id,
                    "document": document.document_id,
                    "dttot_first_name": row_data.get("first_name"),
                    "dttot_middle_name": row_data.get("middle_name"),
                    "dttot_last_name": row_data.get("last_name"),
                    "dttot_alias_name_1": row_data.get("Alias_name_1"),
                    "dttot_first_name_alias_1": row_data.get("first_name_alias_1"),
                    "dttot_middle_name_alias_1": row_data.get("middle_name_alias_1"),
                    "dttot_last_name_alias_1": row_data.get("last_name_alias_1"),
                    "dttot_alias_name_2": row_data.get("Alias_name_2"),
                    "dttot_first_name_alias_2": row_data.get("first_name_alias_2"),
                    "dttot_middle_name_alias_2": row_data.get("middle_name_alias_2"),
                    "dttot_last_name_alias_2": row_data.get("last_name_alias_2"),
                    "dttot_alias_name_3": row_data.get("Alias_name_3"),
                    "dttot_first_name_alias_3": row_data.get("first_name_alias_3"),
                    "dttot_middle_name_alias_3": row_data.get("middle_name_alias_3"),
                    "dttot_last_name_alias_3": row_data.get("last_name_alias_3"),
                    "dttot_alias_name_4": row_data.get("Alias_name_4"),
                    "dttot_first_name_alias_4": row_data.get("first_name_alias_4"),
                    "dttot_middle_name_alias_4": row_data.get("middle_name_alias_4"),
                    "dttot_last_name_alias_4": row_data.get("last_name_alias_4"),
                    "dttot_alias_name_5": row_data.get("Alias_name_5"),
                    "dttot_first_name_alias_5": row_data.get("first_name_alias_5"),
                    "dttot_middle_name_alias_5": row_data.get("middle_name_alias_5"),
                    "dttot_last_name_alias_5": row_data.get("last_name_alias_5"),
                    "dttot_type": row_data.get("Terduga"),
                    "dttot_kode_densus": kode_densus,
                    "dttot_birth_place": row_data.get("Tpt Lahir"),
                    "dttot_birth_date_1": row_data.get("birth_date_1"),
                    "dttot_birth_date_2": row_data.get("birth_date_2"),
                    "dttot_birth_date_3": row_data.get("birth_date_3"),
                    "dttot_nationality_1": row_data.get("WN_1"),
                    "dttot_nationality_2": row_data.get("WN_2"),
                    "dttot_domicile_address": row_data.get("Alamat"),
                    "dttot_description_1": row_data.get("description_1"),
                    "dttot_description_2": row_data.get("description_2"),
                    "dttot_description_3": row_data.get("description_3"),
                    "dttot_description_4": row_data.get("description_4"),
                    "dttot_description_5": row_data.get("description_5"),
                    "dttot_nik_ktp": row_data.get("idNumber"),
                    "dttot_passport_number": row_data.get("passport_number"),
                },
            )
            dttot_serializer = DttotDocSerializer(data=row_data)
            if dttot_serializer.is_valid():
                instance = dttot_serializer.save()
                logger.info(
                    "Successfully saved row data for document ID %s, dttot ID %s",
                    document.document_id, instance.dttot_id,
                )
                return instance.dttot_id

            # Log serializer errors
            errors = dttot_serializer.errors
            error_msg = f"Failed to save DTTOT document data due to validation errors: {errors}"
            logger.error(error_msg)
            raise ValidationError(error_msg)  #noqa: TRY301

        # Optionally, log successful processing and saving of data
        logger.info("DTTOT Document row processing and saving completed successfully.")
        return 0  #noqa: TRY300

    except Exception as e:
        error_msg = f"Error processing row data for document ID {document.document_id}: {e}"
        logger.exception(error_msg)
        raise ValidationError(error_msg) from e
