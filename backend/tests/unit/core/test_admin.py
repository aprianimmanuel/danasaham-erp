"""Test for the Django admin modifications."""

from __future__ import annotations

import shutil
from tempfile import mkdtemp

import pytz  #type: ignore  # noqa: PGH003
from django.contrib.auth import get_user_model  #type: ignore  # noqa: PGH003
from django.core.files.uploadedfile import (  #type: ignore  # noqa: PGH003
    SimpleUploadedFile,
)
from django.test import (  #type: ignore  # noqa: PGH003
    Client,
    TestCase,
    override_settings,
)
from django.urls import reverse  #type: ignore  # noqa: PGH003
from django.utils import timezone  #type: ignore  # noqa: PGH003

from app.documents.models import (  #type: ignore  # noqa: PGH003
    Document,  #type: ignore  # noqa: PGH003
    save_file_to_instance,
)
from app.documents.dttotDoc.models import DttotDoc  #type: ignore  # noqa: PGH003


class DttotDocAdminTest(TestCase):

    def setUp(self) -> None:
        # Create a temporary directory to serve as MEDIA_ROOT
        self.temp_media_dir = mkdtemp()

        # Apply override_settings decorator dynamically
        self.override_media_root = override_settings(MEDIA_ROOT=self.temp_media_dir)
        self.override_media_root.enable()

        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            username="adminuser",
            password="adminpass123",  # noqa: S106
        )
        self.client.force_login(self.admin_user)

        self.normal_user = get_user_model().objects.create_user(
            email="user@example.com",
            username="normaluser",
            password="password123",  # noqa: S106
        )

        self.document_file = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"PDF file content",
            content_type="application/pdf",
        )

        self.document = Document.objects.create(
            document_name="Test Document",
            description="A test document description.",
            document_file=self.document_file,
            document_type="PDF",
            created_by=self.normal_user,
            updated_by=self.normal_user,
        )

        self.dttot_doc = DttotDoc.objects.create(
            user=self.normal_user,
            document=self.document,
            dttot_type="Test Type",
        )

    def tearDown(self) -> None:
        # Restore the original MEDIA_ROOT
        self.override_media_root.disable()

        # Clean up the test media directory content
        shutil.rmtree(self.temp_media_dir, ignore_errors=True)
        super().tearDown()

    def test_list_display(self) -> None:
        """Test that dttotDoc list display includes specific fields."""
        url = reverse("admin:core_dttotdoc_changelist")
        response = self.client.get(url)
        self.assertContains(response, self.dttot_doc.dttot_type)
        self.assertContains(response, self.normal_user.username)

        # Format the date correctly to match the format in the response
        local_tz = pytz.timezone("Asia/Jakarta")  # GMT+7 timezone
        local_time = timezone.localtime(self.dttot_doc.updated_at, local_tz)
        updated_at_date = local_time.strftime("%Y-%m-%d %H:%M:%S")
        self.assertContains(response, f"{updated_at_date} (GMT+7)")

    def test_search_fields(self) -> None:
        """Test the search functionality for dttotDoc in the Django admin."""
        url = reverse("admin:core_dttotdoc_changelist") + "?q=John"
        response = self.client.get(url)
        self.assertContains(response, "John")
        url_doe = reverse("admin:core_dttotdoc_changelist") + "?q=Doe"
        response_doe = self.client.get(url_doe)
        self.assertContains(response_doe, "Doe")

    def test_filters(self) -> None:
        """Test the filters for dttotDoc in the Django admin."""
        url = (
            reverse("admin:core_dttotdoc_changelist")
            + f"?dttot_type={self.dttot_doc.dttot_type}"
        )
        response = self.client.get(url)
        self.assertContains(response, self.dttot_doc.dttot_type)

    def test_change_page(self) -> None:
        """Test that the dttotDoc change page works."""
        url = reverse("admin:core_dttotdoc_change", args=[self.dttot_doc.dttot_id])
        response = self.client.get(url)
        assert response.status_code == 200  # noqa: S101, PLR2004

    def test_create_page(self) -> None:
        """Test the dttotDoc create page."""
        url = reverse("admin:core_dttotdoc_add")
        response = self.client.get(url)
        assert response.status_code == 200  # noqa: S101, PLR2004


class DocumentAdminTest(TestCase):

    def setUp(self) -> None:
        # Create a temporary directory to serve as MEDIA_ROOT
        self.temp_media_dir = mkdtemp()

        # Apply override_settings decorator dynamically
        self.override_media_root = override_settings(MEDIA_ROOT=self.temp_media_dir)
        self.override_media_root.enable()

        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            username="adminuser",
            password="adminpass123",  # noqa: S106
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            email="user@example.com",
            username="normaluser",
            password="password123",  # noqa: S106
        )

        # Add a document_file for the document
        self.document_file = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"",
            content_type="application/pdf",
        )

        self.document = Document.objects.create(
            document_name="Test Document",
            description="A test document description.",
            document_file=self.document_file,
            document_type="PDF",
            created_by=self.user,
            updated_by=self.user,
        )

        # Save the document file using save_file_to_instance
        uploaded_file = SimpleUploadedFile(
            name="test_document.pdf",
            content=b"This is a test document content.",
            content_type="application/pdf",
        )
        save_file_to_instance(self.document, uploaded_file)
        self.document.save()

    def test_documents_list_display(self) -> None:
        """Test that documents are listed with the correct fields in admin."""
        url = reverse("admin:core_document_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.document.document_name)
        self.assertContains(res, self.document.document_type)
        self.assertContains(res, self.user.username)

    def test_document_change_page(self) -> None:
        """Test the document admin change page works."""
        url = reverse("admin:core_document_change", args=[self.document.document_id])
        res = self.client.get(url)

        assert res.status_code == 200  # noqa: S101, PLR2004

    def test_document_add_page(self) -> None:
        """Test the document admin add page works."""
        url = reverse("admin:core_document_add")
        res = self.client.get(url)

        assert res.status_code == 200  # noqa: S101, PLR2004

    def tearDown(self) -> None:
        # Disable the overridden MEDIA_ROOT setting
        self.override_media_root.disable()

        # Remove the temporary directory after the test
        shutil.rmtree(self.temp_media_dir)
