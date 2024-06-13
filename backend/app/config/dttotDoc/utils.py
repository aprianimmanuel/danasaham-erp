import difflib
import logging
from rest_framework.exceptions import ValidationError
from app.config.dttotDoc.serializers import DttotDocSerializer
from app.config.core.models import dttotDoc

logger = logging.getLogger(__name__)

def handle_dttot_document(document, row_data, user_id):
    """
    Processes a given Document object to extract and save detailed data to the dttotDoc model.

    Args:
    document (Document): The document to be processed.
    user_data (dict): Dictionary containing user information.
    df (DataFrame): Processed data as DataFrame

    Raises:
    ValidationError: If there are issues with the data processing that prevent saving.
    """
    try:
        existing_kode_densus = set(
            dttotDoc.objects.values_list(
                'dttot_kode_densus',
                flat=True
            )
        )
        kode_densus = row_data.get('Kode Densus', '')
        if not any(
                difflib.SequenceMatcher(
                    None,
                    kode_densus,
                    existing
                ).ratio() > 0.95 for existing in existing_kode_densus):
            row_data.update({
                'user': user_id,
                'document': document.document_id,
                'dttot_first_name': row_data.get('first_name', None),
                'dttot_middle_name': row_data.get('middle_name', None),
                'dttot_last_name': row_data.get('last_name', None),
                'dttot_alias_name_1': row_data.get('Alias_name_1', None),
                'dttot_first_name_alias_1': row_data.get('first_name_alias_1', None),
                'dttot_middle_name_alias_1': row_data.get('middle_name_alias_1', None),
                'dttot_last_name_alias_1': row_data.get('last_name_alias_1', None),
                'dttot_alias_name_2': row_data.get('Alias_name_2', None),
                'dttot_first_name_alias_2': row_data.get('first_name_alias_2', None),
                'dttot_middle_name_alias_2': row_data.get('middle_name_alias_2', None),
                'dttot_last_name_alias_2': row_data.get('last_name_alias_2', None),
                'dttot_alias_name_3': row_data.get('Alias_name_3', None),
                'dttot_first_name_alias_3': row_data.get('first_name_alias_3', None),
                'dttot_middle_name_alias_3': row_data.get('middle_name_alias_3', None),
                'dttot_last_name_alias_3': row_data.get('last_name_alias_3', None),
                'dttot_alias_name_4': row_data.get('Alias_name_4', None),
                'dttot_first_name_alias_4': row_data.get('first_name_alias_4', None),
                'dttot_middle_name_alias_4': row_data.get('middle_name_alias_4', None),
                'dttot_last_name_alias_4': row_data.get('last_name_alias_4', None),
                'dttot_alias_name_5': row_data.get('Alias_name_5', None),
                'dttot_first_name_alias_5': row_data.get('first_name_alias_5', None),
                'dttot_middle_name_alias_5': row_data.get('middle_name_alias_5', None),
                'dttot_last_name_alias_5': row_data.get('last_name_alias_5', None),
                'dttot_type': row_data.get('Terduga', None),
                'dttot_kode_densus': kode_densus,
                'dttot_birth_place': row_data.get('Tpt Lahir', None),
                'dttot_birth_date_1': row_data.get('birth_date_1', None),
                'dttot_birth_date_2': row_data.get('birth_date_2', None),
                'dttot_birth_date_3': row_data.get('birth_date_3', None),
                'dttot_nationality_1': row_data.get('WN_1', None),
                'dttot_nationality_2': row_data.get('WN_2', None),
                'dttot_domicile_address': row_data.get('Alamat', None),
                'dttot_description_1': row_data.get('description_1', None),
                'dttot_description_2': row_data.get('description_2', None),
                'dttot_description_3': row_data.get('description_3', None),
                'dttot_description_4': row_data.get('description_4', None),
                'dttot_description_5': row_data.get('description_5', None),
                'dttot_nik_ktp': row_data.get('idNumber', None),
                'dttot_passport_number': row_data.get('passport_number', None)
            })
            dttot_serializer = DttotDocSerializer(data=row_data)
            if dttot_serializer.is_valid():
                dttot_serializer.save()
                logger.info(f"Successfully saved row data for document ID {document.document_id}")
            else:
                # Log serializer errors
                errors = dttot_serializer.errors
                error_msg = f"Failed to save DTTOT document data due to validation errors: {errors}"
                logger.error(error_msg)
                raise ValidationError(error_msg)

        # Optionally, log successful processing and saving of data
        logger.info("DTTOT Document row processing and saving completed successfully.")
    except Exception as e:
        logger.error(f"Error processing row data for document ID {document.document_id}: {e}")
        raise
