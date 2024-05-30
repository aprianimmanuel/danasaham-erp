import os
import io
import shutil
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from core.models import dttotDoc
from django.core.files.uploadedfile import SimpleUploadedFile
from openpyxl import Workbook

User = get_user_model()


class DttotDocAPITestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='Testp@ss!23',
            email_verified=True
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)

        # Authenticate the user for all test methods
        self.client.force_authenticate(user=self.user)

        # Create a 'test_media' subdirectory within MEDIA_ROOT for test files
        self.test_media_subdir = 'test_media'
        self.test_media_path = os.path.join(
            settings.MEDIA_ROOT,
            self.test_media_subdir)
        os.makedirs(self.test_media_path, exist_ok=True)

        # Override the MEDIA_ROOT to point to the test media directory
        self.old_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.test_media_path

    def tearDown(self):
        # Clean up the test media directory content
        for item in os.listdir(self.test_media_path):
            path = os.path.join(self.test_media_path, item)
            if os.path.isfile(path) or os.path.islink(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

        # Restore the original MEDIA_ROOT
        settings.MEDIA_ROOT = self.old_media_root
        super().tearDown()

    @staticmethod
    def create_test_document_file():
        output = io.BytesIO()
        wb = Workbook()
        ws = wb.active
        ws.append(["Nama", "Deskripsi", "Terduga", "Kode Densus", "Tpt Lahir", "Tgl Lahir", "WN", "Alamat"])  # noqa
        ws.append([
            "John Doe Alias Don John Alias John Krew",
            "'- NIK nomor: 1234567898765432\n'- paspor nomor: A0987654\n'- pekerjaan: Karyawan Swasta",  # noqa
            "Orang",
            "EDD-013",
            "Surabaya",
            "4 Januari 1973/4 November 1974/4 November 1973",
            "Indonesia",
            "Jalan Getis Gg.III/95A, RT/RW. 013/003, Kel. Lemah Putro, Kec. Sidoarjo, Kab/Kota. Sidoarjo, Prov. Jawa Timur"  # noqa
        ])
        wb.save(output)
        output.seek(0)
        return SimpleUploadedFile(
            "test.xlsx",
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")  # noqa

    def test_create_and_update_dttotDoc(self):
        document_file = self.create_test_document_file()
        upload_response = self.client.post(
            reverse('document-create'),
            {
                'document_file': document_file,
                'document_name': 'Test Document',
                'document_type': 'DTTOT Document',
                'document_file_type': 'XLSX'
            },
            format='multipart'
        )
        self.assertEqual(
            upload_response.status_code,
            status.HTTP_201_CREATED,
            "Document upload failed")
        document_id = upload_response.data['document']['document_id']

        try:
            dttot_doc = dttotDoc.objects.get(document=document_id)
        except dttotDoc.DoesNotExist:
            self.fail(
                "dttotDoc was not automatically created with the document")

        update_url = reverse('dttot-doc-detail', args=[dttot_doc.pk])
        update_data = {
            'dttot_type': 'Updated Type',
            'dttot_first_name': 'UpdatedFirst',
            'dttot_last_name': 'UpdatedSecond',
            'dttot_domicile_address': 'Updated Address',
            'dttot_description_1': 'Updated Description'
        }
        update_response = self.client.patch(
            update_url,
            update_data,
            format='json')
        self.assertEqual(
            update_response.status_code,
            status.HTTP_200_OK,
            "Should return HTTP 200 OK")
        dttot_doc.refresh_from_db()
        self.assertEqual(
            dttot_doc.dttot_type,
            'Updated Type',
            "Check the type of the updated document")
        self.assertEqual(
            dttot_doc.dttot_first_name,
            'UpdatedFirst',
            "Check the updated first name")
