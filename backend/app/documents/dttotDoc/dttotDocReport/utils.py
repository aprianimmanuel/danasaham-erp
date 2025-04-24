from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from django.utils import timezone  # type: ignore  # noqa: PGH003
from docx import Document  # type: ignore  # noqa: PGH003

from app.documents.dttotDoc.dttotDocReportCorporate.models import DttotDocReportCorporate
from app.documents.dttotDoc.dttotDocReportPersonal.models import DttotDocReportPersonal
from app.documents.dttotDoc.dttotDocReportPublisher.models import DttotDocReportPublisher

if TYPE_CHECKING:
    from django.db.models.query import QuerySet  # type: ignore  # noqa: PGH003

    from app.documents.models import Document as DocumentModels
    from app.user.user_profile.models import UserProfile

from django.utils.timezone import now  # type: ignore  # noqa: PGH003


def get_high_score_corporate_entries(  # noqa: D417
        self,  # noqa: ANN001, ARG001
        report: DttotDocReportCorporate,  # The DttotDocReportCorporate object to retrieve entries from.
        threshold: float = 0.85,  # The minimum score match similarity to filter the entries by.
    ) -> QuerySet[DttotDocReportCorporate]:  # A QuerySet of DttotDocReportCorporate objects with a score match similarity greater than the given threshold.
    """Retrieve all DttotDocReportCorporate entries with a score match similarity greater than the given threshold.

    This function will return a QuerySet of DttotDocReportCorporate objects with a score match similarity greater than the given threshold.
    The QuerySet will contain all the entries that have a score match similarity greater than the given threshold.
    The entries in the QuerySet will be sorted in descending order by the score match similarity.

    Parameters
    ----------
        report (DttotDocReportCorporate): The DttotDocReportCorporate object to retrieve entries from.
        threshold (float): The minimum score match similarity to filter the entries by.

    Returns
    -------
        A QuerySet of DttotDocReportCorporate objects with a score match similarity greater than the given threshold.

    """
    return DttotDocReportCorporate.objects.filter(dttotdoc_report=report, score_match_similarity__gt=threshold).order_by('-score_match_similarity')

def get_high_score_personal_entries(  # noqa: D417
        self,  # noqa: ANN001, ARG001
        report: DttotDocReportPersonal,
        threshold: float = 0.85,
) -> QuerySet[DttotDocReportPersonal]:
    """Retrieve all dttotDocReportPersonal entries with a score match similarity greater than the given threshold.

    Args:
    ----
        report: The DttotDocReportPersonal object to retrieve entries from.
        threshold: The minimum score match similarity to filter the entries by.

    Returns:
    -------
        A QuerySet of DttotDocReportPersonal objects with a score match similarity greater than the given threshold.

    """
    return DttotDocReportPersonal.objects.filter(
        dttotdoc_report=report,
        score_match_similarity__gt=threshold,
    )

def get_high_score_publisher_entries(  # noqa: D417
        self,  # noqa: ANN001, ARG001
        report: DttotDocReportPublisher,
        threshold: float = 0.85,
) -> QuerySet[DttotDocReportPublisher]:
    """Retrieve all dttotDocReportPublisher entries with a score match similarity greater than the given threshold.

    Args:
    ----
        report: The DttotDocReportPublisher object to retrieve entries from.
        threshold: The minimum score match similarity to filter the entries by.

    Returns:
    -------
        A QuerySet of DttotDocReportPublisher objects with a score match similarity greater than the given threshold.

    """
    return DttotDocReportPublisher.objects.filter(
        dttotdoc_report=report,
        score_match_similarity__gt=threshold,
    )

def generate_no_issue_report(  # noqa: D417
        self,  # noqa: ANN001, ARG001
        template_path: str,
        context: dict[str, Any],
) -> str:
    """Generate a report using a template file.

    Args:
    ----
        template_path: The path to the template file.
        context: The dictionary with values to replace in the template.

    Returns:
    -------
        The content of the rendered template with replaced values.

    """
    with Path.open(template_path, "r", encoding="utf-8") as template_file:
        content = template_file.read()

    for key, value in context.items():
        content = content.replace(f"{{{{ {key} }}}}", str(value))

    return content

def generate_serta_merta_document(  # noqa: D417
        self,  # noqa: ANN001, ARG001
        entry: DttotDocReportCorporate | DttotDocReportPersonal | DttotDocReportPublisher | DocumentModels,
        template_path: str,
        user_profile: UserProfile,
) -> str:
    """Generate a report using a template file.

    Args:
    ----
        entry: The entry to generate the report for.
        template_path: The path to the template file.
        user_profile: The user profile to generate the report for.
        user_role: The user role to generate the report for.

    Returns:
    -------
        The content of the rendered template with replaced values as a string.

    """
    document = Document(template_path)
    placeholders = {
        "user_full_name": f"{user_profile.first_name} {user_profile.last_name}",
        "user_role_name": user_profile.role_name,
        "user_full_address": (
            f"{user_profile.domicile_address_1} {user_profile.domicile_address_2} "
            f"{user_profile.domicile_address_rt} {user_profile.domicile_address_rw} "
            f"{user_profile.domicile_address_subdistrict} {user_profile.domicile_address_district} "
            f"{user_profile.domicile_address_city} {user_profile.domicile_address_province} "
            f"{user_profile.domicile_address_postal_code}"
        ),
        "created_date_dayname": timezone.now().strftime("%A"),
        "created_date_datenum": timezone.now().strftime("%d"),
        "created_date_monthname": timezone.now().strftime("%B"),
        "created_date_year": timezone.now().strftime("%Y"),
        "created_date_hour": timezone.now().strftime("%H"),
        "created_date_minute": timezone.now().strftime("%M"),
        "dttot_letter_number_updated": entry.dttot_letter_number_reference,
        "police_letter_number_updated": entry.police_letter_date,
        "police_letter_date": entry.police_letter_date,
        "police_letter_about": entry.police_letter_about,
        "user_direct_supervisor_name": user_profile.supervisor_name,
        "user_direct_supervisor_role_name": user_profile.supervisor_role_name,
    }

    for paragraph in document.paragraphs:
        for key, value in placeholders.items():
            if f"{{{{ {key} }}}}" in paragraph.text:
                paragraph.text = paragraph.text.replace(f"{{{{ {key} }}}}", value)

    return document


