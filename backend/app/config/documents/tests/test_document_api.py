from __future__ import annotations

import io
import os
import shutil

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from openpyxl import Workbook
from rest_framework import status
from rest_framework.test import APITestCase

from app.config.core.models import (
    Document,
    User,
    save_file_to_instance,
)


def document_list_url():
    return reverse("documents:document-list")


def document_detail_url(document_id):
    return reverse("documents:document-details", args=[document_id])


class DocumentAPITests(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user("test@example.com", "password123")
        self.client.force_authenticate(user=self.user)

        # Create 'test_media' subdirectory within MEDIA_ROOT for test files
        self.test_media_path = os.path.join(settings.MEDIA_ROOT, "test_media")
        os.makedirs(self.test_media_path, exist_ok=True)

        # Override MEDIA_ROOT to the test directory
        self.old_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.test_media_path

    def tearDown(self) -> None:
        # Clean up the test media directory content
        shutil.rmtree(self.test_media_path, ignore_errors=True)

        # Restore the original MEDIA_ROOT
        settings.MEDIA_ROOT = self.old_media_root
        super().tearDown()

        # Restore the original MEDIA_ROOT
        settings.MEDIA_ROOT = self.old_media_root
        super().tearDown()

    def test_create_document(self) -> None:
        """Test creating a document."""
        self.client.force_authenticate(user=self.user)
        payload = {
            "document_name": "Test Name",
            "document_type": "PDF",
            "description": "Test Description",
            "document_file": SimpleUploadedFile(
                "document.pdf",
                b"Test content",
                content_type="application/pdf",
            ),
        }
        res = self.client.post(document_list_url(), payload, format="multipart")
        assert res.status_code == status.HTTP_201_CREATED
        document = Document.objects.get(pk=res.data["document_id"])
        for key in payload:
            if key != "document_file":
                assert payload[key] == getattr(document, key)
        assert document.document_file

        # Call save_file_to_instance and document.save
        save_file_to_instance(document, payload["document_file"])
        document.save()

        # Verify that the file has been saved correctly
        file_path = document.document_file.path
        assert os.path.exists(file_path)

        # Clean up the saved file
        document.document_file.delete()

    def test_retrieve_documents_list(self) -> None:
        """Test retrieving a list of documents."""
        self.client.force_authenticate(user=self.user)
        Document.objects.create(
            document_name="Test1",
            document_type="PDF",
            created_by=self.user,
            updated_by=self.user,
        )
        Document.objects.create(
            document_name="Test2",
            document_type="DOCX",
            created_by=self.user,
            updated_by=self.user,
        )

        res = self.client.get(document_list_url())
        assert res.status_code == status.HTTP_200_OK
        assert len(res.data) == 2

    def test_retrieve_document_detail(self) -> None:
        """Test retrieving a document's detail."""
        self.client.force_authenticate(user=self.user)
        document = Document.objects.create(
            document_name="Test",
            document_type="PDF",
            created_by=self.user,
            updated_by=self.user,
        )

        url = document_detail_url(document.document_id)
        res = self.client.get(url)
        assert res.status_code == status.HTTP_200_OK
        assert res.data["document_name"] == document.document_name

    def test_update_document(self) -> None:
        """Test updating a document."""
        document = Document.objects.create(
            document_name="Initial Name",
            document_type="PDF",
            created_by=self.user,
            updated_by=self.user,
        )

        payload = {"document_name": "Updated Name", "document_type": "DOCX"}
        url = document_detail_url(document.document_id)
        self.client.force_authenticate(user=self.user)
        res = self.client.patch(url, payload)

        document.refresh_from_db()
        assert res.status_code == status.HTTP_200_OK
        assert document.document_name == payload["document_name"]
        assert document.document_type == payload["document_type"]

    def test_delete_document(self) -> None:
        """Test deleting a document."""
        document = Document.objects.create(
            document_name="Test",
            document_type="PDF",
            created_by=self.user,
            updated_by=self.user,
        )

        url = document_detail_url(document.document_id)
        self.client.force_authenticate(user=self.user)
        res = self.client.delete(url)

        assert res.status_code == status.HTTP_204_NO_CONTENT
        assert not Document.objects.filter(pk=document.pk).exists()


class DTTOTDocumentUploadTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up user that is only run once for all tests in this class
        cls.user = User.objects.create_user(
            "newuser",
            "newuser@example.com",
            "TestP@ss!23",
        )
        cls.document_url = reverse("documents:document-list")

    def setUp(self) -> None:
        super().setUp()
        # Authenticate user
        self.client.force_authenticate(user=self.user)

        # Create 'test_media' subdirectory within MEDIA_ROOT for test files
        self.test_media_subdir = "test_media"
        self.test_media_path = os.path.join(settings.MEDIA_ROOT, "test_media")
        os.makedirs(self.test_media_path, exist_ok=True)

        # Override MEDIA_ROOT to the test directory
        self.old_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.test_media_path

    def tearDown(self) -> None:
        # Restore the original MEDIA_ROOT
        settings.MEDIA_ROOT = self.old_media_root

        # Clean up the test media directory content
        shutil.rmtree(self.test_media_path, ignore_errors=True)
        super().tearDown()

    @staticmethod
    def create_test_document_file():
        # Create an XLSX file in memory
        output = io.BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.append(
            [
                "Nama",
                "Deskripsi",
                "Terduga",
                "Kode Densus",
                "Tpt Lahir",
                "Tgl Lahir",
                "WN",
                "Alamat",
            ],
        )
        ws.append(
            [
                "John Doe Alias Don John Alias John Krew",
                "'- NIK nomor: 1234567898765432\n'- paspor nomor: A0987654\n'- pekerjaan: Karyawan Swasta",
                "Orang",
                "EDD-013",
                "Surabaya",
                "4 Januari 1973/4 November 1974/4 November 1973",
                "Indonesia",
                "Jalan Getis Gg.III/95A, RT/RW. 013/003, Kel. Lemah Putro, Kec. Sidoarjo, Kab/Kota. Sidoarjo, Prov. Jawa Timur",
            ],
        )
        wb.save(output)
        output.seek(0)
        return SimpleUploadedFile(
            "test.xlsx",
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_upload_dttot_document_and_process(self) -> None:
        """Test the upload and processing of a DTTOT Document
        and its saving into the dttotDoc model.
        """
        document_file = self.create_test_document_file()
        with self.settings(MEDIA_ROOT=self.test_media_path):
            response = self.client.post(
                self.document_url,
                {
                    "document_file": document_file,
                    "document_name": "Test Document",
                    "document_type": "DTTOT Document",
                    "document_file_type": "XLSX",
                },
                format="multipart",
            )
            assert response.status_code == status.HTTP_201_CREATED, "Document upload failed"

            # Get document ID from response
            document_id = response.data["document_id"]
            assert document_id is not None, "Document ID was not returned"


class DocumentUploadTests(APITestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        # Setting up user that is only run once for all tests in this class
        cls.user = User.objects.create_user(
            "newuser",
            "newuser@example.com",
            "TestP@ss!23",
        )
        cls.document_url = reverse("documents:document-list")

    def setUp(self) -> None:
        super().setUp()
        # Authenticate user
        self.client.force_authenticate(user=self.user)

        # Create 'test_media' subdirectory within MEDIA_ROOT for test files
        self.test_media_subdir = "test_media"
        self.test_media_path = os.path.join(settings.MEDIA_ROOT, "test_media")
        os.makedirs(self.test_media_path, exist_ok=True)

        # Override MEDIA_ROOT to the test directory
        self.old_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.test_media_path

    def tearDown(self) -> None:
        # Restore the original MEDIA_ROOT
        settings.MEDIA_ROOT = self.old_media_root

        # Clean up the test media directory content
        shutil.rmtree(self.test_media_path, ignore_errors=True)
        super().tearDown()

    @staticmethod
    def create_test_document_file():
        # Create an XLSX file in memory
        output = io.BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.append(
            [
                "Nama",
                "Deskripsi",
                "Terduga",
                "Kode Densus",
                "Tpt Lahir",
                "Tgl Lahir",
                "WN",
                "Alamat",
            ],
        )
        ws.append(
            [
                "John Doe Alias Don John Alias John Krew",
                "'- NIK nomor: 1234567898765432\n'- paspor nomor: A0987654\n'- pekerjaan: Karyawan Swasta",
                "Orang",
                "EDD-013",
                "Surabaya",
                "4 Januari 1973/4 November 1974/4 November 1973",
                "Indonesia",
                "Jalan Getis Gg.III/95A, RT/RW. 013/003, Kel. Lemah Putro, Kec. Sidoarjo, Kab/Kota. Sidoarjo, Prov. Jawa Timur",
            ],
        )
        wb.save(output)
        output.seek(0)
        return SimpleUploadedFile(
            "test.xlsx",
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_upload_dttot_document_and_process(self) -> None:
        document_file = self.create_test_document_file()
        with self.settings(MEDIA_ROOT=self.test_media_path):
            response = self.client.post(
                self.document_url,
                {
                    "document_file": document_file,
                    "document_name": "Test Document",
                    "document_type": "DTTOT Document",
                    "document_file_type": "XLSX",
                },
                format="multipart",
            )
            assert response.status_code == status.HTTP_201_CREATED, "Document upload failed"
            document_id = response.data["document_id"]
            assert document_id is not None, "Document ID was not returned"

            instance = Document.objects.get(pk=document_id)
            save_file_to_instance(instance, document_file)
            instance.save()

            assert Document.objects.filter(pk=document_id).exists(), "Document was not created in the database."
            file_path = instance.document_file.path
            assert os.path.exists(file_path)
            instance.document_file.delete()
