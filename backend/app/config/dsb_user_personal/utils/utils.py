import pandas as pd
from sqlalchemy import create_engine
from app.config.core.models import dsb_user_personal
from tqdm import tqdm
import os

def fetch_data_from_external_db():
    sql_file_path = os.path.join(os.path.dirname(__file__), 'dsb_user_personal.sql')
    with open(sql_file_path, 'r') as file:
        query = file.read()

    # Fetching database connection details from environment variables
    db_host = os.getenv('EXTERNAL_DB_HOST')
    db_name = os.getenv('EXTERNAL_DB_NAME')
    db_port = os.getenv('EXTERNAL_DB_PORT')
    db_user = os.getenv('EXTERNAL_DB_USER')
    db_password = os.getenv('EXTERNAL_DB_PASSWORD')

    # Creating the database engine
    engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

    # Ensure the engine is connected before executing the query
    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection)

    return df

def save_data_to_model(row_data, document, user_id):
    dsb_user_personal.objects.update_or_create(
        personal_nik=row_data['personal_nik'],
        defaults={
            'document': document,
            'user': user_id,
            'user_id': row_data['user_id'],
            'initial_registration_date': row_data['initial_registration_date'],
            'user_name': row_data['user_name'],
            'users_phone_number': row_data['users_phone_number'],
            'users_email_registered': row_data['users_email_registered'],
            'has_email_confirmed': row_data['has_email_confirmed'],
            'users_last_modified_date': row_data['users_last_modified_date'],
            'user_upgrade_to_personal': row_data['user_upgrade_to_personal'],
            'personal_name': row_data['personal_name'],
            'personal_phone_number': row_data['personal_phone_number'],
            'personal_gender': row_data['personal_gender'],
            'personal_birth_date': row_data['personal_birth_date'],
            'personal_spouse_name': row_data['personal_spouse_name'],
            'personal_mother_name': row_data['personal_mother_name'],
            'personal_last_modified_date': row_data['personal_last_modified_date'],
            'personal_domicile_address': row_data['personal_domicile_address'],
            'personal_domicile_address_postalcode': row_data['personal_domicile_address_postalcode'],
            'personal_investment_goals': row_data['personal_investment_goals'],
            'personal_marital_status': row_data['personal_marital_status'],
            'personal_birth_place': row_data['personal_birth_place'],
            'personal_nationality': row_data['personal_nationality'],
            'personal_source_of_fund': row_data['personal_source_of_fund'],
        }
    )
