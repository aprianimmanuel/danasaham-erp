from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

import pandas as pd
from django.db import transaction
from django.utils import timezone
from sqlalchemy import create_engine

from app.config.core.models import Document, User, log_tracker_corporate

logger = logging.getLogger(__name__)

def fetch_data_from_external_db() -> pd.DataFrame:
    sql_file_path = Path(__file__).parent / "log_tracker_corporate.sql"
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
    user: User,
    document: Document,
) -> None:
    with transaction.atomic():
        for _index, row, in df.iterrows():
            # Check if a record with the same corporate_pengurus_id already exist
            existing_record = log_tracker_corporate.objects.filter(core_dsb_user_id=row["user_id"]).first()

            if existing_record:
                # Check if users_last_modified_date is the same
                if existing_record.core_dsb_user_id == row["user_id"]:
                    # Update all fields if core_dsb_user_id is different
                    existing_record.document = document
                    existing_record.last_updated_date = timezone.now()
                    existing_record.last_update_by = user
                    existing_record.corporate_company_name = row["corporate_company_name"]
                    existing_record.initial_registration_date = row["initial_registration_date"]
                    existing_record.corporate_legal_created_date = row["corporate_legal_created_date"]
                    existing_record.corporate_finance_created_date = row["corporate_finance_created_date"]
                    existing_record.corporate_ksei_id_created_date = row["corporate_ksei_id_created_date"]
                    existing_record.corporate_info_check_date = row["corporate_info_check_application_end_date"]
                    existing_record.initial_primary_investment_date = row["initial_primary_investment"]
            else:
                log_tracker_corporate.objects.create(
                    document=document,
                    log_tracker_corporate_id=uuid.uuid4(),
                    created_date=timezone.now(),
                    last_updated_date=None,
                    last_update_by=None,
                    core_dsb_user_id=row["user_id"],
                    corporate_company_name=row["corporate_company_name"],
                    initial_registration_date=row["initial_registration_date"],
                    corporate_legal_created_date=row["corporate_legal_created_date"],
                    corporate_finance_created_date=row["corporate_finance_created_date"],
                    corporate_ksei_id_created_date=row["corporate_ksei_id_created_date"],
                    corporate_info_check_date=row["corporate_info_check_application_end_date"],
                    initial_primary_investment_date=row["initial_primary_investment"],
                )
        logger.info("Successfully processed document ID %s", document)
