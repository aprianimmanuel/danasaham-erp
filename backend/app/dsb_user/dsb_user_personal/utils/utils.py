from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd  #type: ignore # noqa: PGH003
from django.db import transaction  #type: ignore # noqa: PGH003
from sqlalchemy import create_engine  #type: ignore # noqa: PGH003

from app.dsb_user.dsb_user_personal.models import (
    DsbUserPersonal,  #type: ignore # noqa: PGH003
)

if TYPE_CHECKING:
    from app.user.models import User  #type: ignore # noqa: PGH003

logger = logging.getLogger(__name__)


def fetch_data_from_external_db() -> pd.DataFrame:
    sql_file_path = Path(__file__).parent / "dsb_user_personal.sql"
    with sql_file_path.open() as file:
        query = file.read()

    # Fetching database connection details from environment variables
    db_host = os.getenv("EXTERNAL_DB_HOST")
    db_name = os.getenv("EXTERNAL_DB_DATABASE")
    db_port = os.getenv("EXTERNAL_DB_PORT")
    db_user = os.getenv("EXTERNAL_DB_USERNAME")
    db_password = os.getenv("EXTERNAL_DB_PASSWORD")

    # Creating the database engine
    engine = create_engine(
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}",
    )

    # Ensure the engine is connected before executing the query
    with engine.connect() as connection:
        return pd.read_sql_query(query, connection)


def save_data_to_model(
        df: pd.DataFrame,
        document: DsbUserPersonal,
        user: User,
    ) -> None:
    with transaction.atomic():
        for _index, row in df.iterrows():
            # Check if a record with the same coredsb_user_id already exists
            existing_record = DsbUserPersonal.objects.filter(coredsb_user_id=row["user_id"]).first()

            if existing_record:
                # Check if users_last_modified_date is not the same
                if existing_record.users_last_modified_date != row["users_last_modified_date"]:
                    # Update all fields if users_last_modified_date is different
                    existing_record.document = document
                    existing_record.last_update_by = user
                    existing_record.user_name = row["user_name"]
                    existing_record.users_email_registered = row["users_email_registered"]
                    existing_record.users_last_modified_date = row["users_last_modified_date"]
                    existing_record.save()

                # Check if personal_legal_last_modified_date is not the same
                elif existing_record.personal_legal_last_modified_date != row["personal_last_modified_date"]:
                    # Update all fields if personal_legal_last_modified_date is different
                    existing_record.document = document
                    existing_record.last_update_by = user
                    existing_record.user_upgrade_to_personal_date = row["user_upgrade_to_personal_date"]
                    existing_record.personal_name = row["personal_name"]
                    existing_record.personal_phone_number = row["personal_phone_number"]
                    existing_record.personal_nik = row["personal_nik"]
                    existing_record.personal_gender = row["personal_gender"]
                    existing_record.personal_birth_date = row["personal_birth_date"]
                    existing_record.personal_ksei_sre = row["personal_ksei_sre"]
                    existing_record.personal_ksei_sid = row["personal_ksei_sid"]
                    existing_record.personal_spouse_name = row["personal_spouse_name"]
                    existing_record.personal_mother_name = row["personal_mother_name"]
                    existing_record.personal_domicile_address = row["personal_domicile_address"]
                    existing_record.personal_domicile_address_postalcode = row["personal_domicile_address_postalcode"]
                    existing_record.personal_investment_goals = row["personal_investment_goals"]
                    existing_record.personal_marital_status = row["personal_marital_status"]
                    existing_record.personal_birth_place = row["personal_birth_place"]
                    existing_record.personal_nationality = row["personal_nationality"]
                    existing_record.personal_source_of_fund = row["personal_source_of_fund"]
                    existing_record.personal_legal_last_modified_date = row["personal_last_modified_date"]
                    existing_record.save()

                # Check if users_last_modified_date is the same
                elif existing_record.users_last_modified_date == row["users_last_modified_date"]:
                    # Update all fields if users_last_modified_date is different
                    existing_record.document = document
                    existing_record.last_update_by = user
                    existing_record.save()

                # Check if personal_legal_last_modified_date is the same
                elif existing_record.personal_legal_last_modified_date == row["personal_last_modified_date"]:
                    # Update all fields if personal_legal_last_modified_date is different
                    existing_record.document = document
                    existing_record.last_update_by = user
                    existing_record.save()

            else:
                # Save new record if no existing record with the same coredsb_user_id
                DsbUserPersonal.objects.update_or_create(
                    coredsb_user_id=row["user_id"],
                    document=document,
                    last_update_by=None,
                    initial_registration_date=row["initial_registration_date"],
                    user_name=row["user_name"],
                    users_email_registered=row["users_email_registered"],
                    users_last_modified_date=row["users_last_modified_date"],
                    user_upgrade_to_personal_date=row["user_upgrade_to_personal_date"],
                    personal_name=row["personal_name"],
                    personal_phone_number=row["personal_phone_number"],
                    personal_nik=row["personal_nik"],
                    personal_gender=row["personal_gender"],
                    personal_birth_date=row["personal_birth_date"],
                    personal_ksei_sre=row["personal_ksei_sre"],
                    personal_ksei_sid=row["personal_ksei_sid"],
                    personal_spouse_name=row["personal_spouse_name"],
                    personal_mother_name=row["personal_mother_name"],
                    personal_domicile_address=row["personal_domicile_address"],
                    personal_domicile_address_postalcode=row["personal_domicile_address_postalcode"],
                    personal_investment_goals=row["personal_investment_goals"],
                    personal_marital_status=row["personal_marital_status"],
                    personal_birth_place=row["personal_birth_place"],
                    personal_nationality=row["personal_nationality"],
                    personal_source_of_fund=row["personal_source_of_fund"],
                    personal_legal_last_modified_date=row["personal_last_modified_date"],
                )
    logger.info("Successfully processed document ID %s", document.document_id)
