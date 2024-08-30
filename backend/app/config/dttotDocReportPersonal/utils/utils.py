from __future__ import annotations

import difflib
import logging
from datetime import timedelta
from typing import Any

import spacy
from django.utils import timezone

from app.config.core.models import dttotDoc, dttotDocReport, dttotDocReportPersonal

# Constants for default values
SIMILARITY_THRESHOLD = 0.9

# Load the spaCy language model globally
nlp = spacy.load("xx_ent_wiki_sm")

logger = logging.getLogger(__name__)

def calculate_similarity(str1: str | None, str2: str | None) -> float:
    """Calculate the similarity percentage between two strings."""
    # Check if both strings are empty
    if not str1 or not str2:
        return 0.0

    doc1 = nlp(str1)
    doc2 = nlp(str2)
    return doc1.similarity(doc2)


def calculate_token_similarity(str1: str | None, str2: str | None) -> list[float]:
    """Calculate similarity for each token/word in the given strings."""
    # Check if both strings are empty
    if not str1 or not str2:
        return [0.0]

    tokens1 = nlp(str1)
    tokens2 = nlp(str2)
    return [token1.similarity(token2) for token1 in tokens1 for token2 in tokens2]


def get_similarity_scores(
    personal_data: dict[str, str | None],
    dttot: dttotDoc,
) -> dict[str, list[float]]:
    """Calculate the similarity scores for various fields in the personal data against the dttotDoc."""
    fields = {
        "personal_nik_scores": [dttot.dttot_nik_ktp, dttot.dttot_passport_number],
        "user_name_scores": [
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
        "personal_phone_number_scores": [dttot.dttot_passport_number, dttot.dttot_nik_ktp],
        "personal_domicile_address_scores": [dttot.dttot_domicile_address],
        "personal_birth_date_scores": [dttot.dttot_birth_date_1, dttot.dttot_birth_date_2, dttot.dttot_birth_date_3],
        "personal_birth_place_scores": [dttot.dttot_birth_place],
        "personal_spouse_name_scores": [
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
        "personal_mother_name_scores": [
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
        "personal_nationality_scores": [dttot.dttot_nationality_1, dttot.dttot_nationality_2],
        "personal_description_scores": [
            dttot.dttot_description_1, dttot.dttot_description_2, dttot.dttot_description_3,
            dttot.dttot_description_4, dttot.dttot_description_5, dttot.dttot_description_6,
            dttot.dttot_description_7, dttot.dttot_description_8, dttot.dttot_description_9,
        ],
    }

    return {
        key: [max(calculate_token_similarity(personal_data.get(key[:-7], ""), value)) for value in values if value]
        for key, values in fields.items()
    }


def get_aggregated_similarity_score(similarity_scores: dict[str, list[float]]) -> float:
    """Calculate the aggregated similarity score based on the maximum similarity scores for each field."""
    max_scores = {field: max(scores, default=0.0) for field, scores in similarity_scores.items()}

    weights = {
        "personal_nik_scores": 0.4,
        "user_name_scores": 0.3,
        "personal_phone_number_scores": 0.1,
        "personal_domicile_address_scores": 0.02,
        "personal_birth_date_scores": 0.1,
        "personal_birth_place_scores": 0.01,
        "personal_spouse_name_scores": 0.01,
        "personal_mother_name_scores": 0.01,
        "personal_nationality_scores": 0.01,
        "personal_description_scores": 0.04,
    }

    return sum(max_scores[field] * weight for field, weight in weights.items())


def create_dttotdoc_report_personal(
        report_data: dict[str, Any],
    ) -> dttotDocReportPersonal:
    return dttotDocReportPersonal.objects.create(**report_data)


def save_report_data_row_by_row(
    dttotdoc_report: dttotDocReport,
    dsb_user_personal_id: str,
    personal_data: dict[str, Any],
    dttot: dttotDoc,
) -> tuple[dttotDocReportPersonal, str, str]:
    similarity_scores = get_similarity_scores(personal_data, dttot)
    score_match_similarity = get_aggregated_similarity_score(similarity_scores)

    report_data = {
        "dttotdoc_report": dttotdoc_report,
        "dsb_user_personal": dsb_user_personal_id,
        "score_match_similarity": score_match_similarity,
        "kode_densus_personal": dttot.dttot_kode_densus,
    }

    try:
        # Get the current date and calculate the cutoff date for two months ago
        two_months_ago = timezone.now() - timedelta(days=60)

        # Query the existing records
        existing_records = dttotDocReportPersonal.objects.filter(
            kode_densus_personal__in=report_data["kode_densus_personal"],
            dsb_user_personal__in=report_data["dsb_user_personal"],
            created_date__gte=two_months_ago,
        )

        for existing_record in existing_records:
            if (
                difflib.SequenceMatcher(None, report_data["kode_densus_personal"], existing_record.kode_densus_personal).ratio() > SIMILARITY_THRESHOLD and
                difflib.SequenceMatcher(None, report_data["dsb_user_personal"], existing_record.dsb_user_personal).ratio() > SIMILARITY_THRESHOLD
            ):
                # Skip saving if a similar record is found
                return existing_record, "Skipped", "Existing record is similar and was created within the last two months."

        # If no similar record is found, proceed with creating a new one
        return create_dttotdoc_report_personal(report_data)

    except Exception as e:
        logger.exception("Error processing DTTOT Doc Report Personal: %s", str(e))  # noqa: TRY401
        raise
