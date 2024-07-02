from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd
from django.db import transaction
from sqlalchemy import create_engine

from app.config.core.models import dsb_user_personal

logger = logging.getLogger(__name__)


def fetch_data_from_external_db() -> pd.DataFrame:
    sql_file_path = Path(__file__).parent / "dsb_user_personal.sql"
    with sql_file_path.open() as file:
        query = file.read()

    # Fetching database connection details from environment variables
    db_host = os.getenv("EXTERNAL_DB_HOST")
    db_name = os.getenv("EXTERNAL_DB_NAME")
    db_port = os.getenv("EXTERNAL_DB_PORT")
    db_user = os.getenv("EXTERNAL_DB_USER")
    db_password = os.getenv("EXTERNAL_DB_PASSWORD")

    # Creating the database engine
    engine = create_engine(
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
    )

    # Ensure the engine is connected before executing the query
    with engine.connect() as connection:
        return pd.read_sql_query(query, connection)



def save_data_to_model(df: pd.DataFrame, document: dsb_user_personal, user_id: int) -> None:
    with transaction.atomic():
        for _index, row in df.iterrows():
            dsb_user_personal.objects.update_or_create(
                coredsb_user_id=row["user_id"],
                defaults={
                    "document": document,
                    "user": user_id,
                    "initial_registration_date": row["initial_registration_date"],
                    "user_name": row["user_name"],
                    "users_phone_number": row["users_phone_number"],
                    "users_email_registered": row["users_email_registered"],
                    "has_email_confirmed": row["has_email_confirmed"],
                    "users_last_modified_date": row["users_last_modified_date"],
                    "user_upgrade_to_personal": row["user_upgrade_to_personal"],
                    "personal_name": row["personal_name"],
                    "personal_phone_number": row["personal_phone_number"],
                    "personal_nik": row["personal_nik"],
                    "personal_gender": row["personal_gender"],
                    "personal_birth_date": row["personal_birth_date"],
                    "personal_spouse_name": row["personal_spouse_name"],
                    "personal_mother_name": row["personal_mother_name"],
                    "personal_last_modified_date": row["personal_last_modified_date"],
                    "personal_domicile_address": row["personal_domicile_address"],
                    "personal_domicile_address_postalcode": row[
                        "personal_domicile_address_postalcode"
                    ],
                    "personal_investment_goals": row["personal_investment_goals"],
                    "personal_marital_status": row["personal_marital_status"],
                    "personal_birth_place": row["personal_birth_place"],
                    "personal_nationality": row["personal_nationality"],
                    "personal_source_of_fund": row["personal_source_of_fund"],
                    "personal_legal_last_modified_date": row[
                        "personal_last_modified_date"
                    ],
                },
            )
    logger.info("Successfully processed document ID %s", document.document_id)
