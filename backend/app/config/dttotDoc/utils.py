import difflib
from rest_framework.exceptions import ValidationError
from app.config.documents.utils.data_preparation import (
    DTTOTDocumentProcessing,
    ExtractNIKandPassportNumber,
    CleaningSeparatingDeskripsi,
    FormattingColumn
)
from app.config.dttotDoc.serializers import DttotDocSerializer
from app.config.core.models import dttotDoc


def handle_dttot_document(document, user, request):
    """
    Processes a given Document object
    to extract and save detailed data to the dttotDoc model.

    Args:
    document (Document): The document to be processed.
    user (User): The user who initiated the document processing,
    used for tracking.
    context (dict): The context including request, used for serializers.

    Raises:
    ValidationError: If there are issues with the data processing
    that prevent saving.
    """
    if document.document_file and hasattr(document.document_file, 'path'):
        file_path = document.document_file.path
    else:
        raise ValidationError(
            "The document file path is not accessible or the file is not available.")  # noqa

    document_format = document.document_file_type.upper()

    doc_processor = DTTOTDocumentProcessing()
    df = doc_processor.retrieve_data_as_dataframe(file_path, document_format)
    nik_passport_extractor = ExtractNIKandPassportNumber()
    deskripsi_cleaner = CleaningSeparatingDeskripsi()
    formatter = FormattingColumn()

    df = doc_processor.extract_and_split_names(df, name_column='Nama')
    df = deskripsi_cleaner.separating_cleaning_deskripsi(df)
    df = nik_passport_extractor.extract_nik_and_passport_number(df)
    df = formatter.format_birth_date(df)
    df = formatter.format_nationality(df)

    existing_kode_densus = set(
        dttotDoc.objects.values_list(
            'dttot_kode_densus',
            flat=True
        )
    )
    for _, row in df.iterrows():
        kode_densus = row.get('Kode Densus', '')
        if not any(
                difflib.SequenceMatcher(
                    None,
                    kode_densus,
                    existing
                ).ratio() > 0.95 for existing in existing_kode_densus):
            dttot_data = row.to_dict()
            dttot_data.update({
                'user': user.user_id,
                'document': document.document_id,
                'dttot_first_name': row.get('first_name', None),
                'dttot_middle_name': row.get('middle_name', None),
                'dttot_last_name': row.get('last_name', None),
                'dttot_alias_name_1': row.get('Alias_name_1', None),
                'dttot_first_name_alias_1': row.get(
                    'first_name_alias_1', None),
                'dttot_middle_name_alias_1': row.get(
                    'middle_name_alias_1', None),
                'dttot_last_name_alias_1': row.get(
                    'last_name_alias_1', None),
                'dttot_alias_name_2': row.get('Alias_name_2', None),
                'dttot_first_name_alias_2': row.get(
                    'first_name_alias_2', None),
                'dttot_middle_name_alias_2': row.get(
                    'middle_name_alias_2', None),
                'dttot_last_name_alias_2': row.get(
                    'last_name_alias_2', None),
                'dttot_alias_name_3': row.get('Alias_name_3', None),
                'dttot_first_name_alias_3': row.get(
                    'first_name_alias_3', None),
                'dttot_middle_name_alias_3': row.get(
                    'middle_name_alias_3', None),
                'dttot_last_name_alias_3': row.get(
                    'last_name_alias_3', None),
                'dttot_alias_name_4': row.get('Alias_name_4', None),
                'dttot_first_name_alias_4': row.get(
                    'first_name_alias_4', None),
                'dttot_middle_name_alias_4': row.get(
                    'middle_name_alias_4', None),
                'dttot_last_name_alias_4': row.get(
                    'last_name_alias_4', None),
                'dttot_alias_name_5': row.get('Alias_name_5', None),
                'dttot_first_name_alias_5': row.get(
                    'first_name_alias_5', None),
                'dttot_middle_name_alias_5': row.get(
                    'middle_name_alias_5', None),
                'dttot_last_name_alias_5': row.get(
                    'last_name_alias_5', None),
                'dttot_type': row.get('Terduga', None),
                'dttot_kode_densus': kode_densus,
                'dttot_birth_place': row.get('Tpt Lahir', None),
                'dttot_birth_date_1': row.get('birth_date_1', None),
                'dttot_birth_date_2': row.get('birth_date_2', None),
                'dttot_birth_date_3': row.get('birth_date_3', None),
                'dttot_nationality_1': row.get('WN_1', None),
                'dttot_nationality_2': row.get('WN_2', None),
                'dttot_domicile_address': row.get('Alamat', None),
                'dttot_description_1': row.get('description_1', None),
                'dttot_description_2': row.get('description_2', None),
                'dttot_description_3': row.get('description_3', None),
                'dttot_description_4': row.get('description_4', None),
                'dttot_description_5': row.get('description_5', None),
                'dttot_nik_ktp': row.get('idNumber', None),
                'dttot_passport_number': row.get('passport_number', None)
            })
            context = {'request': request}
            dttot_serializer = DttotDocSerializer(
                data=dttot_data,
                context=context)
            if dttot_serializer.is_valid():
                dttot_serializer.save()
            else:
                # Log serializer errors
                # raise a ValidationError with detailed info
                errors = dttot_serializer.errors
                error_msg = f"Failed to save DTTOT document data due to validation errors: {errors}"  # noqa
                raise ValidationError(error_msg)

    # Optionally, log successful processing and saving of data
    print("DTTOT Document processing and saving completed successfully.")
