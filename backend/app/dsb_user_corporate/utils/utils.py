from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd  #type: ignore # noqa: PGH003
from django.db import transaction  #type: ignore # noqa: PGH003
from sqlalchemy import create_engine  #type: ignore # noqa: PGH003

from app.dsb_user_corporate.models import (  #type: ignore # noqa: PGH003
    dsb_user_corporate,
)

if TYPE_CHECKING:
    from app.user.models import User  #type: ignore # noqa: PGH003

logger = logging.getLogger(__name__)


def fetch_data_from_external_db() -> pd.DataFrame:
    sql_file_path = Path(__file__).parent / "corporate_ecf_dttot_check_ver1.sql"
    with sql_file_path.open() as file:
        query = file.read()

    # Fetching database connection details
    db_host = os.getenv("EXTERNAL_DB_HOST")
    db_name = os.getenv("EXTERNAL_DB_DATABASE")
    db_port = os.getenv("EXTERNAL_DB_PORT")
    db_user = os.getenv("EXTERNAL_DB_USERNAME")
    db_password = os.getenv("EXTERNAL_DB_PASSWORD")

    engine = create_engine(
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
    )

    # Ensure the engine is connected before executing the query
    with engine.connect() as connection:
        return pd.read_sql_query(query, connection)



def save_data_to_model(
        df: pd.DataFrame,
        document: dsb_user_corporate,
        user: User) -> None:
    with transaction.atomic():
        for _index, row, in df.iterrows():
            # Check if a record with the same corporate_pengurus_id already exist
            existing_record = dsb_user_corporate.objects.filter(corporate_pengurus_id=row["corporate_pengurus_id"]).first()

            if existing_record:
                # Check if users_last_modified_date is the same
                if existing_record.users_last_modified_date != row["users_last_modified_date"]:
                    # Update all fields if users_last_modified_date is different
                    existing_record.document = document
                    existing_record.last_update_by = user
                    existing_record.initial_registration_date = row["initial_registration_date"]
                    existing_record.user_name = row["user_name"]
                    existing_record.registered_user_email = row["registered_user_email"]
                    existing_record.users_phone_number = row["users_phone_number"]
                    existing_record.users_last_modified_date = row["users_last_modified_date"]
                    existing_record.save()

                # Check if pengurus_last_corporate_last_update_date is the same
                elif existing_record.pengurus_corporate_last_update_date != row["pengurus_corporate_last_update_date"]:
                    # Update all fields if pengurus_last_corporate_date is different
                    existing_record.document = document
                    existing_record.last_update_by = user
                    existing_record.pengurus_corporate_name = row["pengurus_corporate_name"]
                    existing_record.pengurus_corporate_id_number = row["pengurus_corporate_idnumber"]
                    existing_record.pengurus_corporate_phone_number = row["pengurus_corporate_phone_number"]
                    existing_record.pengurus_corporate_place_of_birth = row["pengurus_corporate_place_of_birth"]
                    existing_record.pengurus_corporate_date_of_birth = row["pengurus_corporate_date_of_birth"]
                    existing_record.pengurus_corporate_npwp = row["pengurus_corporate_npwp"]
                    existing_record.pengurus_corporate_domicile_address = row["pengurus_corporate_domicile_address"]
                    existing_record.pengurus_corporate_jabatan = row["pengurus_corporate_jabatan"]
                    existing_record.pengurus_nominal_saham = row["pengurus_nominal_saham"]
                    existing_record.pengurus_corporate_last_update_date = row["pengurus_corporate_last_update_date"]
                    existing_record.save()

                # Check if corporate_legal_last_modified_date is the same
                elif existing_record.corporate_legal_last_modified_date != row["corporate_legal_last_modified_date"]:
                    # Update all fields that being connected to corporate_legal and corporate table if corporate_legal_last_modified date is different
                    existing_record.document = document
                    existing_record.last_update_by = user
                    existing_record.corporate_company_name = row["corporate_company_name"]
                    existing_record.corporate_phone_number = row["corporate_phone_number"]
                    existing_record.corporate_nib = row["corporate_nib"]
                    existing_record.corporate_siup = row["corporate_siup"]
                    existing_record.corporate_skdp = row["corporate_skdp"]
                    existing_record.corporate_legal_last_modified_date = row["corporate_legal_last_modified_date"]
                    existing_record.corporate_asset = row["corporate_asset"]
                    existing_record.corporate_source_of_fund = row["corporate_source_of_fund"]
                    existing_record.corporate_business_field = row["corporate_business_field"]
                    existing_record.corporate_type_of_annual_income = row["corporate_type_of_annual_income"]
                    existing_record.corporate_annual_income = row["corporate_annual_income"]
                    existing_record.corporate_investment_goals = row["corporate_investment_goals"]
            else:
                dsb_user_corporate.objects.update_or_create(
                    corporate_pengurus_id=row["corporate_pengurus_id"],
                    document=document,
                    last_update_by=None,
                    initial_registration_date=row["initial_registration_date"],
                    user_name=row["user_name"],
                    registered_user_email=row["registered_user_email"],
                    users_phone_number=row["users_phone_number"],
                    users_last_modified_date=row["users_last_modified_date"],
                    pengurus_corporate_name=row["pengurus_corporate_name"],
                    pengurus_corporate_id_number=row["pengurus_corporate_id_number"],
                    pengurus_corporate_phone_number=row["pengurus_corporate_phone_number"],
                    pengurus_corporate_place_of_birth=row["pengurus_corporate_place_of_birth"],
                    pengurus_corporate_domicile_address=row["pengurus_corporate_domicile_address"],
                    pengurus_corporate_jabatan=row["pengurus_corporate_jabatan"],
                    pengurus_nominal_saham=row["pengurus_nominal_saham"],
                    pengurus_corporate_last_update_date=row["pengurus_corporate_last_update_date"],
                    users_upgrade_to_corporate_date=row["users_upgrade_to_corporate_date"],
                    corporate_company_name=row["corporate_company_name"],
                    corporate_phone_number=row["corporate_phone_number"],
                    corporate_nib=row["corporate_nib"],
                    corporate_npwp=row["corporate_npwp"],
                    corporate_siup=row["corporate_siup"],
                    corporate_skdp=row["corporate_skdp"],
                    corporate_legal_last_modified_date=row["corporate_legal_last_modified_date"],
                    corporate_domicile_address=row["corporate_domicile_address"],
                    corporate_asset=row["corporate_asset"],
                    corporate_source_of_fund=row["corporate_source_of_fund"],
                    corporate_business_field=row["corporate_business_field"],
                    corporate_type_of_annual_income=row["corporate_type_of_annual_income"],
                    corporate_annual_income=row["corporate_annual_income"],
                    corporate_investment_goals=row["corporate_investment_goals"],
                )
        logger.info("Successfully processed document ID %s", document.document_id)
