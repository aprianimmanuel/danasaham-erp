from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd  #type: ignore # noqa: PGH003
from django.db import transaction  #type: ignore # noqa: PGH003
from sqlalchemy import create_engine  #type: ignore # noqa: PGH003

from app.dsb_user.dsb_user_publisher.models import (  #type: ignore # noqa: PGH003
    DsbUserPublisher,
)

if TYPE_CHECKING:
    from app.user.models import User  #type: ignore # noqa: PGH003

logger = logging.getLogger(__name__)


def fetch_data_from_external_db() -> pd.DataFrame:
    sql_file_path = Path(__file__).parent / "penebit_ecf_dttot_check_ver1.sql"
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


def save_data_to_model(df: pd.DataFrame, document: DsbUserPublisher, user: User) -> None:
    with transaction.atomic():
        for _index, row, in df.iterrows():
            # Check if a record with the same corporate_pengurus_id already exist
            existing_record = DsbUserPublisher.objects.filter(publisher_pengurus_id=row["publisher_pengurus_id"]).first()

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

            # Check if pengurus_publisher_last_modified_date is the same
                elif existing_record.pengurus_publisher_last_modified_date != row["pengurus_publisher_last_modified_date"]:
                    # Update all fields if pengurus_publisher_last_modified_date is different
                    existing_record.document = document
                    existing_record.last_update_by = user
                    existing_record.publisher_pengurus_name = row["publisher_pengurus_name"]
                    existing_record.publisher_pengurus_id_number = row["publisher_pengurus_id_number"]
                    existing_record.publisher_pengurus_phone_number = row["publisher_pengurus_phone_number"]
                    existing_record.publisher_pengurus_role_as = row["publisher_pengurus_role_as"]
                    existing_record.publisher_jabatan_pengurus = row["publisher_jabatan_pengurus"]
                    existing_record.publisher_address_pengurus = row["publisher_address_pengurus"]
                    existing_record.publisher_tempat_lahir_pengurus = row["publisher_tempat_lahir_pengurus"]
                    existing_record.pengurus_publisher_last_modified_date = row["pengurus_publisher_last_modified_date"]
                    existing_record.save()
            else:
                DsbUserPublisher.objects.update_or_create(
                    publisher_pengurus_id=row["publisher_pengurus_id"],
                    document=document,
                    last_update_by=None,
                    initial_registration_date=row["initial_registration_date"],
                    user_name=row["user_name"],
                    registered_user_email=row["registered_user_email"],
                    users_phone_number=row["users_phone_number"],
                    users_last_modified_date=row["users_last_modified_date"],
                    user_upgrade_to_publisher_date=row["user_upgrade_to_publisher_date"],
                    publisher_registered_name=row["publisher_registered_name"],
                    publisher_corporate_type=row["publisher_corporate_type"],
                    publisher_phone_number=row["publisher_phone_number"],
                    publisher_bank_account_number=row["publisher_bank_account_number"],
                    publisher_bank_account_provider_name=row["publisher_bank_account_provider_name"],
                    publisher_business_field=row["publisher_business_field"],
                    publisher_main_business=row["publisher_main_business"],
                    domicile_address_publisher_1=row["domicile_address_publisher_1"],
                    domicile_address_publisher_2=row["domicile_address_publisher_2"],
                    domicile_address_publisher_3_city=row["domicile_address_publisher_3_city"],
                    publisher_last_modified_date=row["publisher_last_modified_date"],
                    publisher_pengurus_name=row["publisher_pengurus_name"],
                    publisher_pengurus_id_number=row["publisher_pengurus_id_number"],
                    publisher_pengurus_phone_number=row["publisher_pengurus_phone_number"],
                    publisher_pengurus_role_as=row["publisher_pengurus_role_as"],
                    publisher_jabatan_pengurus=row["publisher_jabatan_pengurus"],
                    publisher_address_pengurus=row["publisher_address_pengurus"],
                    publisher_tgl_lahir_pengurus=row["publisher_tgl_lahir_pengurus"],
                    publisher_tempat_lahir_pengurus=row["publisher_tempat_lahir_pengurus"],
                    pengurus_publisher_last_modified_date=row["pengurus_publisher_last_modified_date"],
                )
        logger.info("Successfully processed document ID %s", document.document_id)
