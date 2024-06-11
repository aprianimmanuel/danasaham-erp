from celery import shared_task, chain
from app.config.documents.utils.data_preparation import (
    DTTOTDocumentProcessing,
    ExtractNIKandPassportNumber,
    CleaningSeparatingDeskripsi,
    FormattingColumn
)
from app.config.dttotDoc.utils import handle_dttot_document
from app.config.core.models import Document, User
from app.config.dttotDoc.serializers import DttotDocSerializer
from rest_framework.exceptions import ValidationError


@shared_task
def process_dttot_document(document_id, user_id):
    document = Document.objects.get(pk=document_id)
    user = User.objects.get(pk=user_id)
    handle_dttot_document(document, user, {})


@shared_task
def extract_nik_and_passport(document_id):
    document = Document.objects.get(pk=document_id)
    df = DTTOTDocumentProcessing().retrieve_data_as_dataframe(document.document_file.path, document.document_file_type.upper())
    ExtractNIKandPassportNumber().extract_nik_and_passport_number(df)


@shared_task
def clean_and_separate_description(document_id):
    document = Document.objects.get(pk=document_id)
    df = DTTOTDocumentProcessing().retrieve_data_as_dataframe(document.document_file.path, document.document_file_type.upper())
    CleaningSeparatingDeskripsi().separating_cleaning_deskripsi(df)


@shared_task
def format_columns(document_id):
    document = Document.objects.get(pk=document_id)
    df = DTTOTDocumentProcessing().retrieve_data_as_dataframe(document.document_file.path, document.document_file_type.upper())
    FormattingColumn().format_birth_date(df)
    FormattingColumn().format_nationality(df)


@shared_task
def process_dttot_document_workflow(document_id, user_id):
    chain(
        process_dttot_document.s(document_id, user_id),
        extract_nik_and_passport.s(document_id),
        clean_and_separate_description.s(document_id),
        format_columns.s(document_id)
    )()
