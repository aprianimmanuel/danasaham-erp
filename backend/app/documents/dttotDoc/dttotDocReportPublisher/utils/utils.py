from __future__ import annotations

import difflib
import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

import spacy  #type: ignore # noqa: PGH003
from django.utils import timezone  #type: ignore # noqa: PGH003

from app.documents.dttotDoc.dttotDocReportPublisher.models import (  #type: ignore # noqa: PGH003
    DttotDocReportPublisher,  #type: ignore # noqa: PGH003
)

if TYPE_CHECKING:
    from app.documents.dttotDoc.dttotDocReport.models import (
        DttotDocReport,  #type: ignore # noqa: PGH003
    )
    from app.documents.dttotDoc.models import DttotDoc  #type: ignore # noqa: PGH003

SIMILARITY_THRESOLD = 0.9

logger = logging.getLogger(__name__)

# Load the spaCy language model globally
nlp = spacy.load("xx_ent_wiki_sm")

def calculate_similarity(str1: str | None, str2: str | None) -> float:
    """Calculate the similarity percentage between two strings."""
    if not str1 or not str2:
        return 0.0
    doc1 = nlp(str1)
    doc2 = nlp(str2)
    return doc1.similarity(doc2)

# Calculate the similarity for each token/word in the given strings
def calculate_token_similarity(str1: str | None, str2: str | None) -> list[float]:
    """Calculate similarity for each token/word in the given strings."""
    if not str1 or not str2:
        return [0.0]
    tokens1 = nlp(str1)
    tokens2 = nlp(str2)
    return [token1.similarity(token2) for token1 in tokens1 for token2 in tokens2]

def get_similarity_scores(
        publisher_data: dict[str, str | None],
        dttot: DttotDoc,
) -> dict[str, list[float]]:
    """Calculate the similarity scores for various fields in the publisher data against the dttotDoc."""
    fields = {
        "publisher_registered_name_scores": [
            dttot.dttot_first_name, dttot.dttot_middle_name, dttot.dttot_last_name,
            dttot.dttot_alias_name_1, dttot.dttot_alias_first_name_1, dttot.dttot_alias_middle_name_1, dttot.dttot_alias_last_name_1,
            dttot.dttot_alias_name_2, dttot.dttot_alias_first_name_2, dttot.dttot_alias_middle_name_2, dttot.dttot_alias_last_name_2,
            dttot.dttot_alias_name_3, dttot.dttot_alias_first_name_3, dttot.dttot_alias_middle_name_3, dttot.dttot_alias_last_name_3,
            dttot.dttot_alias_name_4, dttot.dttot_alias_first_name_4, dttot.dttot_alias_middle_name_4, dttot.dttot_alias_last_name_4,
            dttot.dttot_alias_name_5, dttot.dttot_alias_first_name_5, dttot.dttot_alias_middle_name_5, dttot.dttot_alias_last_name_5,
            dttot.dttot_alias_name_6, dttot.dttot_alias_first_name_6, dttot.dttot_alias_middle_name_6, dttot.dttot_alias_last_name_6,
            dttot.dttot_alias_name_7, dttot.dttot_alias_first_name_7, dttot.dttot_alias_middle_name_7, dttot.dttot_alias_last_name_7,
            dttot.dttot_alias_name_8, dttot.dttot_alias_first_name_8, dttot.dttot_alias_middle_name_8, dttot.dttot_alias_last_name_8,
            dttot.dttot_alias_name_9, dttot.dttot_alias_first_name_9, dttot.dttot_alias_middle_name_9, dttot.dttot_alias_last_name_9,
            dttot.dttot_alias_name_10, dttot.dttot_alias_first_name_10, dttot.dttot_alias_middle_name_10, dttot.dttot_alias_last_name_10,
            dttot.dttot_alias_name_11, dttot.dttot_alias_first_name_11, dttot.dttot_alias_middle_name_11, dttot.dttot_alias_last_name_11,
            dttot.dttot_alias_name_12, dttot.dttot_alias_first_name_12, dttot.dttot_alias_middle_name_12, dttot.dttot_alias_last_name_12,
            dttot.dttot_alias_name_13, dttot.dttot_alias_first_name_13, dttot.dttot_alias_middle_name_13, dttot.dttot_alias_last_name_13,
            dttot.dttot_alias_name_14, dttot.dttot_alias_first_name_14, dttot.dttot_alias_middle_name_14, dttot.dttot_alias_last_name_14,
            dttot.dttot_alias_name_15, dttot.dttot_alias_first_name_15, dttot.dttot_alias_middle_name_15, dttot.dttot_alias_last_name_15,
            dttot.dttot_alias_name_16, dttot.dttot_alias_first_name_16, dttot.dttot_alias_middle_name_16, dttot.dttot_alias_last_name_16,
            dttot.dttot_alias_name_17, dttot.dttot_alias_first_name_17, dttot.dttot_alias_middle_name_17, dttot.dttot_alias_last_name_17,
            dttot.dttot_alias_name_18, dttot.dttot_alias_first_name_18, dttot.dttot_alias_middle_name_18, dttot.dttot_alias_last_name_18,
            dttot.dttot_alias_name_19, dttot.dttot_alias_first_name_19, dttot.dttot_alias_middle_name_19, dttot.dttot_alias_last_name_19,
            dttot.dttot_alias_name_20, dttot.dttot_alias_first_name_20, dttot.dttot_alias_middle_name_20, dttot.dttot_alias_last_name_20,
            dttot.dttot_alias_name_21, dttot.dttot_alias_first_name_21, dttot.dttot_alias_middle_name_21, dttot.dttot_alias_last_name_21,
            dttot.dttot_alias_name_22, dttot.dttot_alias_first_name_22, dttot.dttot_alias_middle_name_22, dttot.dttot_alias_last_name_22,
            dttot.dttot_alias_name_23, dttot.dttot_alias_first_name_23, dttot.dttot_alias_middle_name_23, dttot.dttot_alias_last_name_23,
            dttot.dttot_alias_name_24, dttot.dttot_alias_first_name_24, dttot.dttot_alias_middle_name_24, dttot.dttot_alias_last_name_24,
            dttot.dttot_alias_name_25, dttot.dttot_alias_first_name_25, dttot.dttot_alias_middle_name_25, dttot.dttot_alias_last_name_25,
            dttot.dttot_alias_name_26, dttot.dttot_alias_first_name_26, dttot.dttot_alias_middle_name_26, dttot.dttot_alias_last_name_26,
            dttot.dttot_alias_name_27, dttot.dttot_alias_first_name_27, dttot.dttot_alias_middle_name_27, dttot.dttot_alias_last_name_27,
            dttot.dttot_alias_name_28, dttot.dttot_alias_first_name_28, dttot.dttot_alias_middle_name_28, dttot.dttot_alias_last_name_28,
        ],
        "publisher_phone_number_scores": [dttot.dttot_passport_number, dttot.dttot_nik_ktp],
        "domicile_address_publisher_1_scores": [dttot.dttot_domicile_address],
        "domicile_address_publisher_2_scores": [dttot.dttot_domicile_address],
        "domicile_address_publisher_3_city_scores": [dttot.dttot_domicile_address],
        "publisher_description_scores": [
            dttot.dttot_description_1, dttot.dttot_description_2, dttot.dttot_description_3,
            dttot.dttot_description_4, dttot.dttot_description_5, dttot.dttot_description_6,
            dttot.dttot_description_7, dttot.dttot_description_8, dttot.dttot_description_9,
        ],
        "publisher_pengurus_names_scores": [
            dttot.dttot_first_name, dttot.dttot_middle_name, dttot.dttot_last_name,
            dttot.dttot_alias_name_1, dttot.dttot_alias_first_name_1, dttot.dttot_alias_middle_name_1, dttot.dttot_alias_last_name_1,
            dttot.dttot_alias_name_2, dttot.dttot_alias_first_name_2, dttot.dttot_alias_middle_name_2, dttot.dttot_alias_last_name_2,
            dttot.dttot_alias_name_3, dttot.dttot_alias_first_name_3, dttot.dttot_alias_middle_name_3, dttot.dttot_alias_last_name_3,
            dttot.dttot_alias_name_4, dttot.dttot_alias_first_name_4, dttot.dttot_alias_middle_name_4, dttot.dttot_alias_last_name_4,
            dttot.dttot_alias_name_5, dttot.dttot_alias_first_name_5, dttot.dttot_alias_middle_name_5, dttot.dttot_alias_last_name_5,
            dttot.dttot_alias_name_6, dttot.dttot_alias_first_name_6, dttot.dttot_alias_middle_name_6, dttot.dttot_alias_last_name_6,
            dttot.dttot_alias_name_7, dttot.dttot_alias_first_name_7, dttot.dttot_alias_middle_name_7, dttot.dttot_alias_last_name_7,
            dttot.dttot_alias_name_8, dttot.dttot_alias_first_name_8, dttot.dttot_alias_middle_name_8, dttot.dttot_alias_last_name_8,
            dttot.dttot_alias_name_9, dttot.dttot_alias_first_name_9, dttot.dttot_alias_middle_name_9, dttot.dttot_alias_last_name_9,
            dttot.dttot_alias_name_10, dttot.dttot_alias_first_name_10, dttot.dttot_alias_middle_name_10, dttot.dttot_alias_last_name_10,
            dttot.dttot_alias_name_11, dttot.dttot_alias_first_name_11, dttot.dttot_alias_middle_name_11, dttot.dttot_alias_last_name_11,
            dttot.dttot_alias_name_12, dttot.dttot_alias_first_name_12, dttot.dttot_alias_middle_name_12, dttot.dttot_alias_last_name_12,
            dttot.dttot_alias_name_13, dttot.dttot_alias_first_name_13, dttot.dttot_alias_middle_name_13, dttot.dttot_alias_last_name_13,
            dttot.dttot_alias_name_14, dttot.dttot_alias_first_name_14, dttot.dttot_alias_middle_name_14, dttot.dttot_alias_last_name_14,
            dttot.dttot_alias_name_15, dttot.dttot_alias_first_name_15, dttot.dttot_alias_middle_name_15, dttot.dttot_alias_last_name_15,
            dttot.dttot_alias_name_16, dttot.dttot_alias_first_name_16, dttot.dttot_alias_middle_name_16, dttot.dttot_alias_last_name_16,
            dttot.dttot_alias_name_17, dttot.dttot_alias_first_name_17, dttot.dttot_alias_middle_name_17, dttot.dttot_alias_last_name_17,
            dttot.dttot_alias_name_18, dttot.dttot_alias_first_name_18, dttot.dttot_alias_middle_name_18, dttot.dttot_alias_last_name_18,
            dttot.dttot_alias_name_19, dttot.dttot_alias_first_name_19, dttot.dttot_alias_middle_name_19, dttot.dttot_alias_last_name_19,
            dttot.dttot_alias_name_20, dttot.dttot_alias_first_name_20, dttot.dttot_alias_middle_name_20, dttot.dttot_alias_last_name_20,
            dttot.dttot_alias_name_21, dttot.dttot_alias_first_name_21, dttot.dttot_alias_middle_name_21, dttot.dttot_alias_last_name_21,
            dttot.dttot_alias_name_22, dttot.dttot_alias_first_name_22, dttot.dttot_alias_middle_name_22, dttot.dttot_alias_last_name_22,
            dttot.dttot_alias_name_23, dttot.dttot_alias_first_name_23, dttot.dttot_alias_middle_name_23, dttot.dttot_alias_last_name_23,
            dttot.dttot_alias_name_24, dttot.dttot_alias_first_name_24, dttot.dttot_alias_middle_name_24, dttot.dttot_alias_last_name_24,
            dttot.dttot_alias_name_25, dttot.dttot_alias_first_name_25, dttot.dttot_alias_middle_name_25, dttot.dttot_alias_last_name_25,
            dttot.dttot_alias_name_26, dttot.dttot_alias_first_name_26, dttot.dttot_alias_middle_name_26, dttot.dttot_alias_last_name_26,
            dttot.dttot_alias_name_27, dttot.dttot_alias_first_name_27, dttot.dttot_alias_middle_name_27, dttot.dttot_alias_last_name_27,
            dttot.dttot_alias_name_28, dttot.dttot_alias_first_name_28, dttot.dttot_alias_middle_name_28, dttot.dttot_alias_last_name_28,
        ],
        "publisher_pengurus_id_number_scores": [dttot.dttot_nik_ktp, dttot.dttot_passport_number],
        "publisher_pengurus_phone_number_scores": [dttot.dttot_passport_number, dttot.dttot_nik_ktp],
        "publisher_address_pengurus_scores": [dttot.dttot_domicile_address],
        "publisher_tgl_lahir_pengurus_scores": [dttot.dttot_birth_date_1, dttot.dttot_birth_date_2, dttot.dttot_birth_date_3],
        "publisher_tempat_lahir_pengurus_scores": [dttot.dttot_birth_place],
        "pengurus_publisher_description_scores": [
            dttot.dttot_description_1, dttot.dttot_description_2, dttot.dttot_description_3,
            dttot.dttot_description_4, dttot.dttot_description_5, dttot.dttot_description_6,
            dttot.dttot_description_7, dttot.dttot_description_8, dttot.dttot_description_9,
        ],
    }

    return {
        key: [max(calculate_token_similarity(publisher_data.get(key[:-7], ""), value)) for value in values if value]
        for key, values in fields.items()
    }

def get_aggregated_similarity_score(
        similarity_scores: dict[str, list[float]],
) -> float:
    """Calculate the aggregated similarity score based on the maximum similarity scores for each fields."""
    max_scores = {field: max(scores, default=0.0) for field, scores in similarity_scores.items()}

    weights = {
        "publisher_registered_name_scores": 0.06,
        "publisher_phone_number_scores": 0.055,
        "domicile_address_publisher_1_scores": 0.06,
        "domicile_address_publisher_2_scores": 0.055,
        "domicile_address_publisher_3_city_scores": 0.06,
        "publisher_description_scores": 0.06,
        "publisher_pengurus_names_scores": 0.06,
        "publisher_pengurus_id_number_scores": 0.25,
        "publisher_pengurus_phone_number_scores": 0.06,
        "publisher_address_pengurus_scores": 0.055,
        "publisher_tgl_lahir_pengurus_scores": 0.06,
        "publisher_tempat_lahir_pengurus_scores": 0.06,
        "pengurus_publisher_description_scores": 0.06,
    }

    return sum(max_scores[field] * weight for field, weight in weights.items())

def create_dttotdoc_report_publisher(
        report_data: dict[str, Any],
) -> DttotDocReportPublisher:
    return DttotDocReportPublisher.objects.create(**report_data)

def save_report_data_row_by_row(
        dttotdoc_report: DttotDocReport,
        dsb_user_publisher_id: str,
        publisher_data: dict[str, Any],
        dttot: DttotDoc,
) -> tuple[DttotDocReportPublisher, str, str]:
    similarity_scores = get_similarity_scores(publisher_data, dttot)
    score_match_similarity = get_aggregated_similarity_score(similarity_scores)

    report_data = {
        "dttotdoc_report": dttotdoc_report,
        "dsb_user_publisher": dsb_user_publisher_id,
        "score_match_similarity": score_match_similarity,
        "kode_densus_publisher": dttot.dttot_kode_densus,
    }

    try:
        # Get the current date and calculate the cutoff date for two months ago
        twomonths = timezone.now() - timedelta(days=60)

        # Query the existing records
        existing_records = DttotDocReportPublisher.objects.filter(
            kode_densus_publisher__in=report_data["kode_densus_publisher"],
            dsb_user_publisher__in=report_data["dsb_user_publisher"],
            created_date__gte=twomonths,
        )

        for existing_record in existing_records:
            if (
                difflib.SequenceMatcher(None, report_data["kode_densus_publisher"], existing_record.kode_densus_publisher).ratio() > SIMILARITY_THRESOLD and
                difflib.SequenceMatcher(None, report_data["dsb_user_publisher"], existing_record.dsb_user_publisher).ratio() > SIMILARITY_THRESOLD
            ):
                # Skip saving the record if it is similar to an existing record
                return existing_record, "Skipped", "Existing record is similar and was created within the last two months."

        return create_dttotdoc_report_publisher(report_data)

    except Exception:
        logger.exception("Error processing DTTOT Doc Report Publisher: %s")
        raise

