from django.test import TestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch

from app.documents.models import Document
from .models import DttotDocReport
# It's good practice to patch the handlers where they are looked up (i.e., in the signals module if they are connected there)
# or where they are defined and imported from if you are testing the connection logic itself.
# Since ready() connects them, we patch them in the .signals module.

User = get_user_model()

class DttotDocReportSignalTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', password='password')
        # Assuming Document has minimal required fields like 'doc_type'.
        # Adjust if Document model has other required fields.
        cls.document = Document.objects.create(doc_name="Test Document", doc_type="TEST_TYPE", created_by=cls.user)

    def setUp(self):
        # This report is created fresh for each test, ensuring no state leakage.
        self.report = DttotDocReport.objects.create(
            document=self.document,
            last_update_by=self.user,
            status_doc="INITIALIZED"
        )

    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_failed')
    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_done')
    def test_status_changes_to_failed_sends_signal(self, mock_handle_done, mock_handle_failed):
        self.report.status_doc = "FAILED"
        self.report.save()
        mock_handle_failed.assert_called_once_with(sender=DttotDocReport, instance=self.report)
        mock_handle_done.assert_not_called()

    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_failed')
    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_done')
    def test_status_changes_to_done_sends_signal(self, mock_handle_done, mock_handle_failed):
        self.report.status_doc = "DONE"
        self.report.save()
        mock_handle_done.assert_called_once_with(sender=DttotDocReport, instance=self.report)
        mock_handle_failed.assert_not_called()

    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_failed')
    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_done')
    def test_status_changes_to_other_does_not_send_signal(self, mock_handle_done, mock_handle_failed):
        self.report.status_doc = "PROCESSING"
        self.report.save()
        mock_handle_failed.assert_not_called()
        mock_handle_done.assert_not_called()

    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_failed')
    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_done')
    def test_status_already_failed_no_signal_on_save(self, mock_handle_done, mock_handle_failed):
        self.report.status_doc = "FAILED"
        self.report.save() # First save, signal should be sent
        mock_handle_failed.assert_called_once_with(sender=DttotDocReport, instance=self.report)
        mock_handle_done.assert_not_called()

        # Reset mocks and save again
        mock_handle_failed.reset_mock()
        mock_handle_done.reset_mock()

        self.report.save() # Save again with status still FAILED
        mock_handle_failed.assert_not_called()
        mock_handle_done.assert_not_called()

    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_failed')
    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_done')
    def test_status_already_done_no_signal_on_save(self, mock_handle_done, mock_handle_failed):
        self.report.status_doc = "DONE"
        self.report.save() # First save, signal should be sent
        mock_handle_done.assert_called_once_with(sender=DttotDocReport, instance=self.report)
        mock_handle_failed.assert_not_called()

        # Reset mocks and save again
        mock_handle_failed.reset_mock()
        mock_handle_done.reset_mock()

        self.report.save() # Save again with status still DONE
        mock_handle_failed.assert_not_called()
        mock_handle_done.assert_not_called()

    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_failed')
    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_done')
    def test_new_instance_saved_as_failed_sends_signal(self, mock_handle_done, mock_handle_failed):
        # Create a new instance directly with FAILED status
        new_report = DttotDocReport(
            document=self.document,
            last_update_by=self.user,
            status_doc="FAILED"  # Set status before first save
        )
        new_report.save()
        mock_handle_failed.assert_called_once_with(sender=DttotDocReport, instance=new_report)
        mock_handle_done.assert_not_called()

    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_failed')
    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_done')
    def test_new_instance_saved_as_done_sends_signal(self, mock_handle_done, mock_handle_failed):
        # Create a new instance directly with DONE status
        new_report = DttotDocReport(
            document=self.document,
            last_update_by=self.user,
            status_doc="DONE"  # Set status before first save
        )
        new_report.save()
        mock_handle_done.assert_called_once_with(sender=DttotDocReport, instance=new_report)
        mock_handle_failed.assert_not_called()

    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_failed')
    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_done')
    def test_status_changes_from_none_to_failed(self, mock_handle_done, mock_handle_failed):
        report_no_status = DttotDocReport.objects.create(
            document=self.document,
            last_update_by=self.user,
            status_doc=None
        )
        report_no_status.status_doc = "FAILED"
        report_no_status.save()
        mock_handle_failed.assert_called_once_with(sender=DttotDocReport, instance=report_no_status)
        mock_handle_done.assert_not_called()

    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_failed')
    @patch('app.documents.dttotDoc.dttotDocReport.signals.handle_status_done')
    def test_status_changes_from_none_to_done(self, mock_handle_done, mock_handle_failed):
        report_no_status = DttotDocReport.objects.create(
            document=self.document,
            last_update_by=self.user,
            status_doc=None
        )
        report_no_status.status_doc = "DONE"
        report_no_status.save()
        mock_handle_done.assert_called_once_with(sender=DttotDocReport, instance=report_no_status)
        mock_handle_failed.assert_not_called()

```
