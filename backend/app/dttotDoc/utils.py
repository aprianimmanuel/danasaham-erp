from rest_framework.exceptions import ValidationError
from documents.utils.data_preparation import (
    DTTOTDocumentProcessing,
    ExtractNIKandPassportNumber,
    CleaningSeparatingDeskripsi,
    FormattingColumn)
from dttotDoc.serializers import DttotDocSerializer
from core.models import Document


def handle_dttot_document(document, user):
    """
    Processes a given Document object to extract and save detailed data to the dttotDoc model.

    Args:
    document (Document): The document to be processed.
    user (User): The user who initiated the document processing, used for tracking.

    Raises:
    ValidationError: If there are issues with the data processing that prevent saving.
    """
    if document.document_file and hasattr(document.document_file, 'path'):
        file_path = document.document_file.path
    else:
        # Handle the case where the document file path is not directly accessible
        raise ValidationError("The document file path is not accessible or the file is not available.")

    document_format = document.document_file_type.upper()

    # Initialize and apply processing utilities
    doc_processor = DTTOTDocumentProcessing()
    df = doc_processor.retrieve_data_as_dataframe(file_path, document_format)
    nik_passport_extractor = ExtractNIKandPassportNumber()
    deskripsi_cleaner = CleaningSeparatingDeskripsi()
    formatter = FormattingColumn()

    df = nik_passport_extractor.extract_nik_and_passport_number(df)
    df = deskripsi_cleaner.separating_cleaning_deskripsi(df)
    df = formatter.format_birth_date(df)
    df = formatter.format_nationality(df)

    # Iterate over DataFrame rows and save dttotDoc records
    for _, row in df.iterrows():
        dttot_data = {
            'input_by': user,
            'document_id': document.document_id,
            '_dttot_first_name': row.get('first_name', ''),
            '_dttot_middle_name': row.get('middle_name', ''),
            '_dttot_last_name': row.get('last_name', ''),
            'dttot_type': row.get('Terduga', ''),
            '_dttot_domicile_address1': row.get('domicile_address1', ''),
            'dttot_domicile_rt': row.get('domicile_rt', None),
            'dttot_domicile_rw': row.get('domicile_rw', None),
            'dttot_domicile_kelurahan': row.get('domicile_kelurahan', ''),
            'dttot_domicile_kecamatan': row.get('domicile_kecamatan', ''),
            'dttot_domicile_kabupaten': row.get('domicile_kabupaten', ''),
            'dttot_domicile_kota': row.get('domicile_kota', ''),
            'dttot_domicile_provinsi': row.get('domicile_provinsi', ''),
            'dttot_domicile_postal_code': row.get('domicile_postal_code', None),
            'dttot_domicile_country': row.get('domicile_country', ''),
            '_dttot_nik_ktp': row.get('idNumber', ''),
            '_dttot_passport_number': row.get('passport_number', ''),
            'dtott_job': row.get('job', ''),
            '_dttot_mobile_number': row.get('mobile_number', ''),
            '_dttot_organization_name': row.get('organization_name', ''),
        }

        dttot_serializer = DttotDocSerializer(data=dttot_data)
        if dttot_serializer.is_valid():
            dttot_serializer.save()
        else:
            # Proper error handling
            raise ValidationError(dttot_serializer.errors)
