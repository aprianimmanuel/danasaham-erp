from __future__ import annotations

import difflib
import logging
from typing import Any

from django.core.exceptions import (  #type: ignore # noqa: PGH003
    MultipleObjectsReturned,
    ObjectDoesNotExist,
)
from rest_framework.exceptions import ValidationError  #type: ignore # noqa: PGH003

from app.documents.dttotDoc.models import DttotDoc  #type: ignore # noqa: PGH003
from app.documents.dttotDoc.serializers import (
    DttotDocSerializer,  #type: ignore # noqa: PGH003
)

logger = logging.getLogger(__name__)

MAGIC_COMPARISON_RATIO: float = 0.95

def handle_dttot_document(document: Any, row_data: dict[str, Any], user_data: str) -> str:
    try:
        existing_kode_densus = set(
            DttotDoc.objects.values_list("dttot_kode_densus", flat=True),
        )
        kode_densus = row_data.get("Kode Densus", "")
        existing_dttot_doc = None

        # Check if an existing record with a similar kode_densus exists
        for existing in existing_kode_densus:
            if difflib.SequenceMatcher(None, kode_densus, existing).ratio() > MAGIC_COMPARISON_RATIO:
                try:
                    # attempt strict get
                    existing_dttot_doc = DttotDoc.objects.get(dttot_kode_densus=existing)
                except MultipleObjectsReturned:
                    # log detail and pick the first one
                    matching_docs = DttotDoc.objects.filter(dttot_kode_densus=existing)
                    if matching_docs.exists():
                        existing_dttot_doc = matching_docs.first()
                        # Optional: log warning with document IDs
                        logger.warning(
                            f"Multiple DttotDoc entries found for kode_densus '{existing}', using the first one. IDs: {[str(doc.id) for doc in matching_docs]}",  # noqa: G004
                        )
                    else:
                        msg = f"Unexpected error: MultipleObjectsReturned for '{existing}' but queryset returned nothing."
                        raise ValidationError(  # noqa: B904
                            msg,
                        )
                except ObjectDoesNotExist:
                    existing_dttot_doc = None
                break

        # If a similar record exists, update it
        if existing_dttot_doc:
            row_data["document"] = document.document_id
            row_data["last_update_by"] = user_data
            serializer = DttotDocSerializer(existing_dttot_doc,data=row_data)
        else:
            # Else, create a new record
            row_data.update({
                "last_update_by": user_data,
                "document": document.document_id,
                "dttot_first_name": row_data.get("first_name"),
                "dttot_middle_name": row_data.get("middle_name"),
                "dttot_last_name": row_data.get("last_name"),
                "dttot_alias_name_1": row_data.get("Alias_name_1"),
                "dttot_alias_first_name_1": row_data.get("first_name_alias_1"),
                "dttot_alias_middle_name_1": row_data.get("middle_name_alias_1"),
                "dttot_alias_last_name_1": row_data.get("last_name_alias_1"),
                "dttot_alias_name_2": row_data.get("Alias_name_2"),
                "dttot_alias_first_name_2": row_data.get("first_name_alias_2"),
                "dttot_alias_middle_name_2": row_data.get("middle_name_alias_2"),
                "dttot_alias_last_name_2": row_data.get("last_name_alias_2"),
                "dttot_alias_name_3": row_data.get("Alias_name_3"),
                "dttot_alias_first_name_3": row_data.get("first_name_alias_3"),
                "dttot_alias_middle_name_3": row_data.get("middle_name_alias_3"),
                "dttot_alias_last_name_3": row_data.get("last_name_alias_3"),
                "dttot_alias_name_4": row_data.get("Alias_name_4"),
                "dttot_alias_first_name_4": row_data.get("first_name_alias_4"),
                "dttot_alias_middle_name_4": row_data.get("middle_name_alias_4"),
                "dttot_alias_last_name_4": row_data.get("last_name_alias_4"),
                "dttot_alias_name_5": row_data.get("Alias_name_5"),
                "dttot_alias_first_name_5": row_data.get("first_name_alias_5"),
                "dttot_alias_middle_name_5": row_data.get("middle_name_alias_5"),
                "dttot_alias_last_name_5": row_data.get("last_name_alias_5"),
                "dttot_alias_name_6": row_data.get("Alias_name_6"),
                "dttot_alias_first_name_6": row_data.get("first_name_alias_6"),
                "dttot_alias_middle_name_6": row_data.get("middle_name_alias_6"),
                "dttot_alias_last_name_6": row_data.get("last_name_alias_6"),
                "dttot_alias_name_7": row_data.get("Alias_name_7"),
                "dttot_alias_first_name_7": row_data.get("first_name_alias_7"),
                "dttot_alias_middle_name_7": row_data.get("middle_name_alias_7"),
                "dttot_alias_last_name_7": row_data.get("last_name_alias_7"),
                "dttot_alias_name_8": row_data.get("Alias_name_8"),
                "dttot_alias_first_name_8": row_data.get("first_name_alias_8"),
                "dttot_alias_middle_name_8": row_data.get("middle_name_alias_8"),
                "dttot_alias_last_name_8": row_data.get("last_name_alias_8"),
                "dttot_alias_name_9": row_data.get("Alias_name_9"),
                "dttot_alias_first_name_9": row_data.get("first_name_alias_9"),
                "dttot_alias_middle_name_9": row_data.get("middle_name_alias_9"),
                "dttot_alias_last_name_9": row_data.get("last_name_alias_9"),
                "dttot_alias_name_10": row_data.get("Alias_name_10"),
                "dttot_alias_first_name_10": row_data.get("first_name_alias_10"),
                "dttot_alias_middle_name_10": row_data.get("middle_name_alias_10"),
                "dttot_alias_last_name_10": row_data.get("last_name_alias_10"),
                "dttot_alias_name_11": row_data.get("Alias_name_11"),
                "dttot_alias_first_name_11": row_data.get("first_name_alias_11"),
                "dttot_alias_middle_name_11": row_data.get("middle_name_alias_11"),
                "dttot_alias_last_name_11": row_data.get("last_name_alias_11"),
                "dttot_alias_name_12": row_data.get("Alias_name_12"),
                "dttot_alias_first_name_12": row_data.get("first_name_alias_12"),
                "dttot_alias_middle_name_12": row_data.get("middle_name_alias_12"),
                "dttot_alias_last_name_12": row_data.get("last_name_alias_12"),
                "dttot_alias_name_13": row_data.get("Alias_name_13"),
                "dttot_alias_first_name_13": row_data.get("first_name_alias_13"),
                "dttot_alias_middle_name_13": row_data.get("middle_name_alias_13"),
                "dttot_alias_last_name_13": row_data.get("last_name_alias_13"),
                "dttot_alias_name_14": row_data.get("Alias_name_14"),
                "dttot_alias_first_name_14": row_data.get("first_name_alias_14"),
                "dttot_alias_middle_name_14": row_data.get("middle_name_alias_14"),
                "dttot_alias_last_name_14": row_data.get("last_name_alias_14"),
                "dttot_alias_name_15": row_data.get("Alias_name_15"),
                "dttot_alias_first_name_15": row_data.get("first_name_alias_15"),
                "dttot_alias_middle_name_15": row_data.get("middle_name_alias_15"),
                "dttot_alias_last_name_15": row_data.get("last_name_alias_15"),
                "dttot_alias_name_16": row_data.get("Alias_name_16"),
                "dttot_alias_first_name_16": row_data.get("first_name_alias_16"),
                "dttot_alias_middle_name_16": row_data.get("middle_name_alias_16"),
                "dttot_alias_last_name_16": row_data.get("last_name_alias_16"),
                "dttot_alias_name_17": row_data.get("Alias_name_17"),
                "dttot_alias_first_name_17": row_data.get("first_name_alias_17"),
                "dttot_alias_middle_name_17": row_data.get("middle_name_alias_17"),
                "dttot_alias_last_name_17": row_data.get("last_name_alias_17"),
                "dttot_alias_name_18": row_data.get("Alias_name_18"),
                "dttot_alias_first_name_18": row_data.get("first_name_alias_18"),
                "dttot_alias_middle_name_18": row_data.get("middle_name_alias_18"),
                "dttot_alias_last_name_18": row_data.get("last_name_alias_18"),
                "dttot_alias_name_19": row_data.get("Alias_name_19"),
                "dttot_alias_first_name_19": row_data.get("first_name_alias_19"),
                "dttot_alias_middle_name_19": row_data.get("middle_name_alias_19"),
                "dttot_alias_last_name_19": row_data.get("last_name_alias_19"),
                "dttot_alias_name_20": row_data.get("Alias_name_20"),
                "dttot_alias_first_name_20": row_data.get("first_name_alias_20"),
                "dttot_alias_middle_name_20": row_data.get("middle_name_alias_20"),
                "dttot_alias_last_name_20": row_data.get("last_name_alias_20"),
                "dttot_alias_name_21": row_data.get("Alias_name_21"),
                "dttot_alias_first_name_21": row_data.get("first_name_alias_21"),
                "dttot_alias_middle_name_21": row_data.get("middle_name_alias_21"),
                "dttot_alias_last_name_21": row_data.get("last_name_alias_21"),
                "dttot_alias_name_22": row_data.get("Alias_name_22"),
                "dttot_alias_first_name_22": row_data.get("first_name_alias_22"),
                "dttot_alias_middle_name_22": row_data.get("middle_name_alias_22"),
                "dttot_alias_last_name_22": row_data.get("last_name_alias_22"),
                "dttot_alias_name_23": row_data.get("Alias_name_23"),
                "dttot_alias_first_name_23": row_data.get("first_name_alias_23"),
                "dttot_alias_middle_name_23": row_data.get("middle_name_alias_23"),
                "dttot_alias_last_name_23": row_data.get("last_name_alias_23"),
                "dttot_alias_name_24": row_data.get("Alias_name_24"),
                "dttot_alias_first_name_24": row_data.get("first_name_alias_24"),
                "dttot_alias_middle_name_24": row_data.get("middle_name_alias_24"),
                "dttot_alias_last_name_24": row_data.get("last_name_alias_24"),
                "dttot_alias_name_25": row_data.get("Alias_name_25"),
                "dttot_alias_first_name_25": row_data.get("first_name_alias_25"),
                "dttot_alias_middle_name_25": row_data.get("middle_name_alias_25"),
                "dttot_alias_last_name_25": row_data.get("last_name_alias_25"),
                "dttot_alias_name_26": row_data.get("Alias_name_26"),
                "dttot_alias_first_name_26": row_data.get("first_name_alias_26"),
                "dttot_alias_middle_name_26": row_data.get("middle_name_alias_26"),
                "dttot_alias_last_name_26": row_data.get("last_name_alias_26"),
                "dttot_alias_name_27": row_data.get("Alias_name_27"),
                "dttot_alias_first_name_27": row_data.get("first_name_alias_27"),
                "dttot_alias_middle_name_27": row_data.get("middle_name_alias_27"),
                "dttot_alias_last_name_27": row_data.get("last_name_alias_27"),
                "dttot_alias_name_28": row_data.get("Alias_name_28"),
                "dttot_alias_first_name_28": row_data.get("first_name_alias_28"),
                "dttot_alias_middle_name_28": row_data.get("middle_name_alias_28"),
                "dttot_alias_last_name_28": row_data.get("last_name_alias_28"),
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
                "dttot_description_6": row_data.get("description_6"),
                "dttot_description_7": row_data.get("description_7"),
                "dttot_description_8": row_data.get("description_8"),
                "dttot_description_9": row_data.get("description_9"),
                "dttot_nik_ktp": row_data.get("idNumber"),
                "dttot_passport_number": row_data.get("passport_number"),
            })
            serializer = DttotDocSerializer(data=row_data)

        if serializer.is_valid():
            instance = serializer.save()
            logger.info(
                "Successfully saved row data for document ID %s, dttot ID %s",
                document.document_id, instance.dttot_id,
            )
            return instance.dttot_id

        # Log serializer errors
        errors = serializer.errors
        error_msg = f"Failed to save DTTOT document data due to validation errors: {errors}"
        logger.error(error_msg)
        raise ValidationError(error_msg)  # noqa: TRY301

    except Exception as e:
        error_msg = f"Error processing row data for document ID {document.document_id}: {e}"
        logger.exception(error_msg)
        raise ValidationError(error_msg) from e
