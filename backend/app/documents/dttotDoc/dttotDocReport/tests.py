import os
from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch, mock_open, MagicMock
from django.conf import settings
from django.db import DatabaseError # For simulating SQL execution errors

from app.documents.models import Document
from .models import DttotDocReport
from .signals import get_sql_command # Import for direct testing

User = get_user_model()

# Define these based on the actual content of your report_signals.sql
# These are placeholders as per the subtask description for report_signals.sql creation.
# If the actual file has, e.g., "SELECT 'FAILED SQL';", update these constants.
EXPECTED_FAILED_SQL = "UPDATE some_table SET status = 'Error' WHERE report_id = %s;"
EXPECTED_DONE_SQL = "UPDATE some_table SET status = 'Completed' WHERE report_id = %s;"

# Path to the SQL file, similar to signals.py
SQL_FILE_PATH_IN_TESTS = os.path.join(
    settings.BASE_DIR,
    "app",
    "documents",
    "dttotDoc",
    "dttotDocReport",
    "utils",
    "report_signals.sql"
)

class DttotDocReportSignalAndSqlTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password')
        cls.document = Document.objects.create(doc_name="Test Document", doc_type="TEST_TYPE", created_by=cls.user)

        # Ensure the SQL file exists with placeholder content for tests that rely on it.
        # This step assumes the file was created in a previous subtask.
        # For truly isolated tests, you might create a temporary mock file here.
        # For now, we rely on its presence from the previous step.
        if not os.path.exists(SQL_FILE_PATH_IN_TESTS):
            # Fallback: create a dummy version if it's missing, to prevent test setup crashes.
            # This is a safeguard; ideally, the file should exist.
            os.makedirs(os.path.dirname(SQL_FILE_PATH_IN_TESTS), exist_ok=True)
            with open(SQL_FILE_PATH_IN_TESTS, 'w') as f:
                f.write("-- SQL for FAILED status\n")
                f.write(f"{EXPECTED_FAILED_SQL}\n\n")
                f.write("-- SQL for DONE status\n")
                f.write(f"{EXPECTED_DONE_SQL}\n")


    def setUp(self):
        self.report = DttotDocReport.objects.create(
            document=self.document,
            last_update_by=self.user,
            status_doc="INITIALIZED"
        )

    @patch('app.documents.dttotDoc.dttotDocReport.signals.connection')
    def test_status_changes_to_failed_executes_sql(self, mock_db_connection):
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__.return_value = mock_cursor

        self.report.status_doc = "FAILED"
        self.report.save()

        mock_db_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(EXPECTED_FAILED_SQL, [self.report.dttotdoc_report_id])

    @patch('app.documents.dttotDoc.dttotDocReport.signals.connection')
    def test_status_changes_to_done_executes_sql(self, mock_db_connection):
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__.return_value = mock_cursor

        self.report.status_doc = "DONE"
        self.report.save()

        mock_db_connection.cursor.assert_called_once()
        mock_cursor.execute.assert_called_once_with(EXPECTED_DONE_SQL, [self.report.dttotdoc_report_id])

    @patch('app.documents.dttotDoc.dttotDocReport.signals.connection')
    def test_status_changes_to_other_does_not_execute_sql(self, mock_db_connection):
        self.report.status_doc = "PROCESSING"
        self.report.save()
        mock_db_connection.cursor.assert_not_called()

    @patch('app.documents.dttotDoc.dttotDocReport.signals.connection')
    def test_status_already_failed_no_sql_on_second_save(self, mock_db_connection):
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__.return_value = mock_cursor

        self.report.status_doc = "FAILED"
        self.report.save() # First save, SQL should execute
        mock_cursor.execute.assert_called_once_with(EXPECTED_FAILED_SQL, [self.report.dttotdoc_report_id])

        mock_db_connection.reset_mock() # Reset the main connection mock
        mock_cursor.reset_mock() # Reset the cursor mock itself
        mock_db_connection.cursor.return_value.__enter__.return_value = mock_cursor # Re-assign after reset

        self.report.save() # Save again with status still FAILED
        mock_db_connection.cursor.assert_not_called() # No new cursor needed
        mock_cursor.execute.assert_not_called() # SQL should not execute again


    @patch('app.documents.dttotDoc.dttotDocReport.signals.connection')
    def test_new_instance_saved_as_failed_executes_sql(self, mock_db_connection):
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__.return_value = mock_cursor

        new_report = DttotDocReport(
            document=self.document,
            last_update_by=self.user,
            status_doc="FAILED"
        )
        new_report.save()
        mock_cursor.execute.assert_called_once_with(EXPECTED_FAILED_SQL, [new_report.dttotdoc_report_id])

    @patch('app.documents.dttotDoc.dttotDocReport.signals.connection')
    def test_failed_sql_execution_error_is_logged(self, mock_db_connection):
        mock_cursor = MagicMock()
        mock_db_connection.cursor.return_value.__enter__.return_value = mock_cursor
        mock_cursor.execute.side_effect = DatabaseError("Test DB Error")

        with self.assertLogs(logger='app.documents.dttotDoc.dttotDocReport.signals', level='ERROR') as cm:
            self.report.status_doc = "FAILED"
            self.report.save()

        self.assertIn(f"Error executing FAILED SQL command for DttotDocReport {self.report.dttotdoc_report_id}: Test DB Error", cm.output[0])
        mock_cursor.execute.assert_called_once()

    # --- Tests for get_sql_command ---

    @patch('app.documents.dttotDoc.dttotDocReport.signals.os.path.exists', return_value=False)
    def test_get_sql_command_file_not_found(self, mock_exists):
        with self.assertLogs(logger='app.documents.dttotDoc.dttotDocReport.signals', level='ERROR') as cm:
            sql = get_sql_command("FAILED")
        self.assertIsNone(sql)
        self.assertIn(f"SQL file not found: {SQL_FILE_PATH_IN_TESTS}", cm.output[0])

    def test_get_sql_command_status_marker_not_found(self):
        # Assuming SQL_FILE_PATH_IN_TESTS exists and has FAILED/DONE blocks
        with self.assertLogs(logger='app.documents.dttotDoc.dttotDocReport.signals', level='INFO') as cm:
            sql = get_sql_command("NON_EXISTENT_STATUS")
        self.assertIsNone(sql)
        self.assertIn("No SQL command found for status 'NON_EXISTENT_STATUS'", cm.output[0])

    @patch('builtins.open', new_callable=mock_open, read_data="-- SQL for FAILED status\n\n-- SQL for DONE status\n")
    def test_get_sql_command_empty_sql_block(self, mock_file_open):
         # This test relies on the specific parsing logic of get_sql_command
        with self.assertLogs(logger='app.documents.dttotDoc.dttotDocReport.signals', level='INFO') as cm:
            sql = get_sql_command("FAILED") # Marker exists, but no actual SQL lines after it
        self.assertIsNone(sql) # Expect None because no actual command lines were collected
        self.assertIn("No SQL command found for status 'FAILED'", cm.output[0])


    @patch('builtins.open', new_callable=mock_open, read_data="-- SQL for FAILED status\nSELECT * FROM failed_table;\n-- Another comment\nSELECT 1;\n\n-- SQL for DONE status\nSELECT * FROM done_table;")
    def test_get_sql_command_parses_correctly(self, mock_file_open):
        sql_failed = get_sql_command("FAILED")
        self.assertEqual(sql_failed, "SELECT * FROM failed_table; SELECT 1;")
        # Note: The current get_sql_command joins lines. If it should handle multi-line SQL differently, this test would change.
        # And it strips comments like "-- Another comment" if they are on their own line.

        sql_done = get_sql_command("DONE")
        self.assertEqual(sql_done, "SELECT * FROM done_table;")

    @patch('app.documents.dttotDoc.dttotDocReport.signals.os.path.exists', return_value=True)
    @patch('builtins.open', side_effect=IOError("Disk read error"))
    def test_get_sql_command_io_error(self, mock_file_open, mock_exists):
        with self.assertLogs(logger='app.documents.dttotDoc.dttotDocReport.signals', level='ERROR') as cm:
            sql = get_sql_command("FAILED")
        self.assertIsNone(sql)
        self.assertIn(f"Error reading SQL file {SQL_FILE_PATH_IN_TESTS}: Disk read error", cm.output[0])

```
