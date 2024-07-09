from  __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd
from django.db import transaction
from sqlalchemy import create_engine

from app.config.core.models import dsb_user_corporate

logger = logging.getLogger(__name__)


def fetch_data_from_external_db() -> pd.DataFrame:
    sql_file_path = Path(__file__).parent / "corporate_ecf_dttot_check_ver1.sql"
    with sql_file_path.open() as file:
        query = file.read()

    # Fetching database connection details
    db_host = os.getenv("EXTERNAL_DB_HOST")
    db_name = os.getenv("EXTERNAL_DB_NAME")
    db_port = os.getenv("EXTERNAL_DB_PORT")
    db_user = os.getenv("EXTERNAL_DB_USER")
    db_password = os.getenv("EXTERNAL_DB_PASSWORD")

    engine = create_engine(
        f"postgresql://{db_user}:{db_password}@{db_port}/{db_name}"
    )

    # Ensure the engine is connected before executing the query
    with engine.connect() as connection:
        return pd.read_sql_query(query, connection)


def save_data_to_model(df: pd.DataFrame, document:dsb_user_corporate, user_id:str) -> None:
    with transaction.atomic():
        for _index, row, in df.iterrows():
            dsb_user_corporate.objects.update_or_create(
                corporate_pengurus_id=row["corporate_pengurus_id"],
                defaults={
                    "document": document,
                    "user": user_id,
                    "initial_registration_date": row["initial_registration_date"],
                    "user_name": row["user_name"],
                    "registered_user_email": row["registered_user_email"],
                    "users_phone_number": row["users_phone_number"],
                    "users_last_modified_date": row["users_last_modified_date"],
                    "corporate_pengurus_id": row["corporate_pengurus_id"],
                    "pengurus_corporate_name": row["pengurus_corporate_name"],
                    "pengurus_corporate_id_number": row["pengurus_corporate_id_number"],
                    "pengurus_corporate_place_of_birth": row["pengurus_corporate_place_of_birth"],
                    "pengurus_corporate_npwp": row["pengurus_corporate_npwp"],
                    "pengurus_corporate_domicile_address": row["pengurus_corporate_domicile_address"],
                    "pengurus_corporate_jabatan": row["pengurus_corporate_jabatan"],
                    "pengurus_nominal_saham": row["pengurus_nominal_saham"],
                    "pengurus_corporate_last_update_date": row["pengurus_corporate_last_update_date"],
                    "user_upgrade_to_corporate": row["users_upgrade_to_corporate"],
                    "corporate_company_name": row["corporate_company_name"],
                    "corporate_phone_number": row["corporate_phone_number"],
                    "corporate_nib": row["corporate_nib"],
                    "corporate_npwp": row["corporate_npwp"],
                    "corporate_siup": row["corporate_siup"],
                    "corporate_skdp": row["corporate_skdp"],
                    "corporate_legal_last_modified_date": row["corporate_legal_last_modified_date"],
                    "corporate_domicile_address": row["corporate_domicile_address"],
                    "corporate_asset": row["corporate_asset"],
                    "corporate_source_of_fund": row["corporate_source_of_fund"],
                    "corporate_business_field": row["corporate_business_field"],
                    "corporate_type_of_annual_income": row["corporate_type_of_annual_income"],
                    "corporate_annual_income": row["corporate_annual_income"],
                    "corporate_investment_goals": row["corporate_investment_goals"]
                }
            )
    logger.info("Successfully processed document ID %s", document.document_id)