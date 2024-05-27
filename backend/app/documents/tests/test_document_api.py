import io
import shutil
from tempfile import TemporaryDirectory
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.contrib.auth import get_user_model
from core.models import Document, dttotDoc, User
from django.conf import settings
from openpyxl import Workbook


def document_list_url():
    return reverse('document-create')


def document_detail_url(document_pk):
    return reverse('document-detail', args=[document_pk])


def dttot_process_url(document_pk):
    return reverse('dttot-process', args=[document_pk])


def document_create_url():
    return reverse('document-create')


class DocumentAPITests(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'test@example.com', 'password123')

    def tearDown(self):
        # Cleanup the MEDIA_ROOT directory after each test
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)

    def test_create_document(self):
        """Test creating a document."""
        self.client.force_authenticate(user=self.user)
        payload = {
            'document_name': 'Test Name',
            'document_type': 'PDF',
            'description': 'Test Description',
            'document_file': SimpleUploadedFile(
                'document.pdf',
                b'Test content',
                content_type='application/pdf')
        }
        res = self.client.post(
            document_create_url(),
            payload,
            format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        document = Document.objects.get(pk=res.data['document_id'])
        for key in payload.keys():
            if key != 'document_file':
                self.assertEqual(payload[key], getattr(document, key))
        self.assertTrue(document.document_file)

    def test_retrieve_documents_list(self):
        """Test retrieving a list of documents."""
        self.client.force_authenticate(user=self.user)
        Document.objects.create(
            document_name='Test1',
            document_type='PDF',
            created_by=self.user,
            updated_by=self.user)
        Document.objects.create(
            document_name='Test2',
            document_type='DOCX',
            created_by=self.user,
            updated_by=self.user)

        res = self.client.get(document_list_url())
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_retrieve_document_detail(self):
        """Test retrieving a document's detail."""
        self.client.force_authenticate(user=self.user)
        document = Document.objects.create(
            document_name='Test',
            document_type='PDF',
            created_by=self.user,
            updated_by=self.user)

        url = document_detail_url(document.pk)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['document_name'], document.document_name)

    def test_update_document(self):
        """Test updating a document."""
        document = Document.objects.create(
            document_name='Initial Name',
            document_type='PDF',
            created_by=self.user,
            updated_by=self.user)

        payload = {'document_name': 'Updated Name', 'document_type': 'DOCX'}
        url = document_detail_url(document.pk)
        self.client.force_authenticate(user=self.user)
        res = self.client.patch(url, payload)

        document.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(document.document_name, payload['document_name'])
        self.assertEqual(document.document_type, payload['document_type'])

    def test_delete_document(self):
        """Test deleting a document."""
        document = Document.objects.create(
            document_name='Test',
            document_type='PDF',
            created_by=self.user,
            updated_by=self.user)

        url = document_detail_url(document.pk)
        self.client.force_authenticate(user=self.user)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Document.objects.filter(
                pk=document.pk).exists())


class DTTOTDocumentUploadTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Setting up user that is only run once for all tests in this class
        cls.user = User.objects.create_user(
            'newuser',
            'newuser@example.com',
            'TestP@ss!23')
        cls.document_url = reverse('document-create')

    def setUp(self):
        super().setUp()
        # Authenticate user
        self.client.force_authenticate(user=self.user)

        # Set up a temporary directory for MEDIA_ROOT
        self.temp_media_dir = TemporaryDirectory()
        self.addCleanup(self.temp_media_dir.cleanup)  # Ensure cleanup

        # Set up a document to be uploaded
        self.document_file = self.create_test_document_file()

    @staticmethod
    def create_test_document_file():
        # Create an XLSX file in memory
        output = io.BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.append(["Nama", "Deskripsi", "Terduga", "Kode Densus", "Tpt Lahir", "Tgl lahir", "WN", "Alamat"])  # noqa
        ws.append(
            [
                "John Doe Alias Don John Alias John Krew",
                "'- NIK nomor: 1234567898765432\n'- paspor nomor: A0987654\n'- pekerjaan: Karyawan Swasta",  # noqa
                "Orang",
                "EDD-013",
                "Surabaya",
                "4 Januari 1973/4 November 1974/4 November 1973",
                "Indonesia",
                "Jalan Getis Gg.III/95A, RT/RW. 013/003, Kel. Lemah Putro, Kec. Sidoarjo, Kab/Kota. Sidoarjo, Prov. Jawa Timur"  # noqa
            ]
        )
        wb.save(output)
        output.seek(0)
        return SimpleUploadedFile(
            "test.xlsx",
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")  # noqa

    def test_upload_dttot_document_and_process(self):
        """Test the upload and processing of a DTTOT Document and its saving into the dttotDoc model."""  # noqa
        with self.settings(MEDIA_ROOT=self.temp_media_dir.name):
            response = self.client.post(
                self.document_url,
                {'document_file': self.document_file},
                format='multipart'
            )
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Document upload failed")

            # Get document ID from response
            document_id = response.data.get('document_id')
            self.assertIsNotNone(document_id, "Document ID was not returned")

            # Check if document and its associated dttotDoc entry was created
            self.assertTrue(
                Document.objects.filter(pk=document_id).exists(),
                "Document was not created in the database.")
            self.assertTrue(
                dttotDoc.objects.filter(document_id=document_id).exists(),
                "DTTOT Doc entry was not created.")
