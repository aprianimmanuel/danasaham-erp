import logging
import os
from django.dispatch import Signal
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)

dttot_doc_report_status_failed = Signal()
dttot_doc_report_status_done = Signal()

SQL_FILE_PATH = os.path.join(
    settings.BASE_DIR,
    "app",
    "documents",
    "dttotDoc",
    "dttotDocReport",
    "utils",
    "report_signals.sql"
)

def get_sql_command(status: str) -> str | None:
    """
    Retrieves an SQL command from the predefined SQL file based on the status.
    """
    marker = f"-- SQL for {status.upper()} status"
    sql_command_lines = []
    in_command_block = False

    try:
        if not os.path.exists(SQL_FILE_PATH):
            logger.error(f"SQL file not found: {SQL_FILE_PATH}")
            return None

        with open(SQL_FILE_PATH, 'r') as f:
            for line in f:
                stripped_line = line.strip()
                if stripped_line == marker:
                    in_command_block = True
                    sql_command_lines = []  # Reset for current block
                    continue

                if in_command_block:
                    if not stripped_line or stripped_line.startswith("--"):
                        # End of current block if it's empty or another comment
                        if sql_command_lines: # Check if we actually collected lines
                            break
                        else: # If no lines collected yet, it might be a comment within the block, so continue
                            if stripped_line.startswith("-- SQL for"): # it's another marker
                                break
                            else: # it's a comment like "-- Example:"
                                continue

                    # Only add non-empty, non-comment lines unless it's the start of another command block
                    if stripped_line and not stripped_line.startswith("--"):
                         sql_command_lines.append(stripped_line)
                    elif stripped_line.startswith("-- SQL for"): # Reached next marker
                        break


        if not sql_command_lines:
            logger.info(f"No SQL command found for status '{status}' in {SQL_FILE_PATH} under marker '{marker}'.")
            return None

        return " ".join(sql_command_lines)

    except IOError as e:
        logger.error(f"Error reading SQL file {SQL_FILE_PATH}: {e}")
        return None
    except Exception as e:
        logger.error(f"An unexpected error occurred in get_sql_command: {e}")
        return None


def handle_status_failed(sender, instance, **kwargs):
    """Handles the DttotDocReport status changed to FAILED event."""
    logger.info(f"DttotDocReport status changed to FAILED for instance: {instance.dttotdoc_report_id}")

    sql_command = get_sql_command("FAILED")
    if sql_command:
        try:
            with connection.cursor() as cursor:
                # Assuming the SQL command uses %s as a placeholder for the report ID.
                # instance.dttotdoc_report_id is the primary key of DttotDocReport
                cursor.execute(sql_command, [instance.dttotdoc_report_id])
            logger.info(f"Successfully executed FAILED SQL command for DttotDocReport: {instance.dttotdoc_report_id}")
        except Exception as e:
            logger.error(f"Error executing FAILED SQL command for DttotDocReport {instance.dttotdoc_report_id}: {e}\nSQL: {sql_command}")
    else:
        logger.info(f"No FAILED SQL command configured or found for DttotDocReport: {instance.dttotdoc_report_id}")


def handle_status_done(sender, instance, **kwargs):
  """Handles the DttotDocReport status changed to DONE event."""
  logger.info(f"DttotDocReport status changed to DONE for instance: {instance.dttotdoc_report_id}")

  sql_command = get_sql_command("DONE")
  if sql_command:
    try:
        with connection.cursor() as cursor:
            # Assuming the SQL command uses %s as a placeholder for the report ID.
            cursor.execute(sql_command, [instance.dttotdoc_report_id])
        logger.info(f"Successfully executed DONE SQL command for DttotDocReport: {instance.dttotdoc_report_id}")
    except Exception as e:
        logger.error(f"Error executing DONE SQL command for DttotDocReport {instance.dttotdoc_report_id}: {e}\nSQL: {sql_command}")
  else:
    logger.info(f"No DONE SQL command configured or found for DttotDocReport: {instance.dttotdoc_report_id}")
