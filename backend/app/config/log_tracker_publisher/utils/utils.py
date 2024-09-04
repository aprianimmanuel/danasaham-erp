from __future__ import annotations

import logging
import os
import uuid
from pathlib import Path

import pandas as pd
from django.db import transaction
from django.utils import timezone
from sqlalchemy import create_engine

from app.config.core.models import User, log_tracker_publisher

logger = logging.getLogger(__name__)


def fetch_data_from_external_db() -> pd.DataFrame:
    sql_file_path = Path(__file__).parent / "log_tracker_publisher.sql"
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
    document: log_tracker_publisher,
) -> None:
    with transaction.atomic():
        for _index, row, in df.iterrows():
            # Check if a record with the same corporate_pengurus_id already exist
            existing_record = log_tracker_publisher.objects.filter(core_dsb_user_id=row["user_id"]).first()

            if existing_record:
                # Check if users_last_modified_date is the same
                if existing_record.core_dsb_user_id != row["user_id"]:
                    # Update all fields if core_dsb_user_id is different
                    existing_record.document = document
                    existing_record.log_tracker_publisher_id = uuid.uuid4()
                    existing_record.created_date = timezone.now()
                    existing_record.last_updated_date = None
                    existing_record.last_update_by = None
                    existing_record.core_dsb_user_id = row["core_dsb_user_id"]
                    existing_record.publisher_company_name = row["publisher_company_name"]
                    existing_record.initial_registration_date = row["initial_registration_date"]
                    existing_record.publisher_upgrade_date = row["publisher_created_date"]
                    existing_record.publisher_legal_data_input_created_date = row["publisher_legal_created_date"]
                    existing_record.publisher_finance_data_input_created_date = row["publisher_finance_created_date"]
                    existing_record.publisher_proposal_data_input_created_date = row["publisher_proposal_created_date"]
                    existing_record.primary_va_registration_registration_date = row["primary_va_registration_created_date"]
                    existing_record.va_operational_approval_created_date = row["va_operational_approval"]
                    existing_record.approval_registration_fee_date = row["approval_registration_fee"]
                    existing_record.primary_offering_input_date = row["primary_offering_input"]
                    existing_record.confirmation_primary_offering_date = row["confirmation_primary_offering"]
                    existing_record.cbestreporting_date = row["cbestreporting"]
                    existing_record.investation_succcess_sk_upload_date = row["investation_success_sk_upload"]
                    existing_record.investation_success_check_date = row["investation_success_check"]
                    existing_record.investation_success_approval_date = row["investation_success_approval"]
                    existing_record.investation_success_fund_transfer_date = row["investation_success_fund_transfer"]
                    existing_record.investation_success_share_distribution_date = row["investation_success_share_distribution"]
            else:
                log_tracker_publisher.objects.update(
                    document=document,
                    last_updated_date=timezone.now(),
                    last_update_by=user,
                    core_dsb_user_id=row["user_id"],
                    publisher_company_name=row["publisher_company_name"],
                    initial_registration_date=row["initial_registration_date"],
                    publisher_upgrade_date=row["publisher_created_date"],
                    publisher_legal_data_input_created_date=row["publisher_legal_created_date"],
                    publisher_finance_data_input_created_date=row["publisher_finance_created_date"],
                    publisher_proposal_data_input_created_date=row["publisher_proposal_created_date"],
                    primary_va_registration_registration_date=row["primary_va_registration_created_date"],
                    va_operational_approval_created_date=row["va_operational_approval"],
                    approval_registration_fee_date=row["approval_registration_fee"],
                    primary_offering_input_date=row["primary_offering_input"],
                    confirmation_primary_offering_date=row["confirmation_primary_offering"],
                    cbestreporting_date=row["cbestreporting"],
                    investation_succcess_sk_upload_date=row["investation_success_sk_upload"],
                    investation_success_check_date=row["investation_success_check"],
                    investation_success_approval_date=row["investation_success_approval"],
                    investation_success_fund_transfer_date=row["investation_success_fund_transfer"],
                    investation_success_share_distribution_date=row["investation_success_share_distribution"],
                )
        logger.info("Successfully processed document ID %s", document)
