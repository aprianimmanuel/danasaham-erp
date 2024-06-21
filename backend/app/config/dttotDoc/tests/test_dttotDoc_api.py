import os
import io
import shutil
import pytest
from unittest.mock import patch, MagicMock
from time import sleep
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from app.config.core.models import Document, dttotDoc
from django.core.files.uploadedfile import SimpleUploadedFile
from openpyxl import Workbook
from app.config.dttotDoc.tasks import process_dttot_document
from app.config.documents.signals import dttot_document_created


User = get_user_model()


@pytest.mark.django_db
@pytest.mark.usefixtures(
    'celery_session_app',
    'celery_session_worker',
    'celery_config',
    'celery_parameters',
    'celery_enable_logging',
    'use_celery_app_trap')
class DttotDocAPITestCase(APITestCase):

    @pytest.fixture(autouse=True, scope='class')
    def setup_celery_worker(self, celery_session_worker):
        self.celery_worker = celery_session_worker

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email='test@example.com', username='testuser', password='Testp@ss!23')
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.force_authenticate(user=self.user)
        self.test_media_subdir = 'test_media'
        self.test_media_path = os.path.join(settings.MEDIA_ROOT, self.test_media_subdir)
        os.makedirs(self.test_media_path, exist_ok=True)
        self.old_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = self.test_media_path

    def tearDown(self):
        for item in os.listdir(self.test_media_path):
            path = os.path.join(self.test_media_path, item)
            if os.path.isfile(path) or os.path.islink(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
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
        return SimpleUploadedFile("test.xlsx", output.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    @patch('app.config.dttotDoc.tasks.process_dttot_document_row.delay')
    @patch('app.config.dttotDoc.tasks.process_dttot_document.delay')
    async def test_create_and_update_dttotDoc(self, mock_process_dttot_document, mock_process_dttot_document_row):
        document_file = self.create_test_document_file()
        with self.settings(MEDIA_ROOT=self.test_media_path):
            upload_response = self.client.post(
                reverse('documents:document-list'),
                {
                    'document_file': document_file,
                    'document_name': 'Test Document',
                    'document_type': 'DTTOT Document',
                    'document_file_type': 'XLSX'
                },
                format='multipart'
            )
            self.assertEqual(upload_response.status_code, status.HTTP_201_CREATED, "Document upload failed")
            document_id = upload_response.data['document_id']

            # Trigger the Celery task
            user_data = {'user_id': str(self.user.user_id)}
            await dttot_document_created.asend_robust(sender=Document, instance=Document.objects.get(pk=document_id), created=True, context={}, user_data=user_data)

            # Wait for the Celery task to complete
            sleep(2)

            # Verify that the Celery task has been called
            mock_process_dttot_document_row.assert_called()

            response = self.client.get(reverse('dttotdocs:dttot-doc-list', kwargs={'document_id': document_id}))
            self.assertEqual(response.status_code, status.HTTP_200_OK, "dttotDoc was not automatically created with the document")

            dttot_docs = response.data
            self.assertTrue(dttot_docs, "dttotDoc was not found in the response")

            dttot_doc = dttot_docs[0]
            self.assertEqual(dttot_doc['document'], document_id, "Document ID does not match")
            self.assertIn('dttot_id', dttot_doc, "dttot_id not found in the response")
            self.assertIn('document_data', dttot_doc, "document_data not found in the response")
            self.assertIn('updated_at', dttot_doc, "updated_at not found in the response")
            self.assertIn('user', dttot_doc, "user not found in the response")

            update_url = reverse('dttotdocs:dttot-doc-detail', kwargs={'dttot_id': dttot_doc['dttot_id']})
            update_data = {
                'dttot_type': 'Updated Type',
                'dttot_first_name': 'UpdatedFirst',
                'dttot_last_name': 'UpdatedSecond',
                'dttot_domicile_address': 'Updated Address',
                'dttot_description_1': 'Updated Description'
            }
            update_response = self.client.patch(update_url, update_data, format='json')
            self.assertEqual(update_response.status_code, status.HTTP_200_OK, "Should return HTTP 200 OK")

            dttot_doc = self.client.get(update_url).data
            self.assertEqual(dttot_doc['dttot_type'], 'Updated Type', "Check the type of the updated document")
            self.assertEqual(dttot_doc['dttot_first_name'], 'UpdatedFirst', "Check the updated first name")


class DttotDocReportTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls):
        # Setting up user that is only run once for all tests in this class
        cls.user = User.objects.create_user(
            'newuser',
            'newuser@example.com',
            'TestP@ss!23'
        )
        cls.document_url = reverse('document-create')

    def setUp(self):
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
        ws.append(["Nama", "Deskripsi", "Terduga", "Kode Densus", "Tpt Lahir", "Tgl Lahir", "WN", "Alamat"])  # noqa
        data = [
            ["John Doe Alias Don John Alias John Krew",
             "'- NIK nomor: 1234567898765432\n'- paspor nomor: A0987654\n'- pekerjaan: Karyawan Swasta",  # noqa
             "Orang", "EDD-013", "Surabaya", "4 Januari 1973/4 November 1974/4 November 1973", "Indonesia",  # noqa
             "Jalan Getis Gg.III/95A, RT/RW. 013/003, Kel. Lemah Putro, Kec. Sidoarjo, Kab/Kota. Sidoarjo, Prov. Jawa Timur"],  # noqa
            ["Jane Mary alias Maria Yan Alias Yan Smith",
             "'- Nomor Paspor: B 0897455\n'- tanggal 5 agustus 2011 menuju Malaysia\n'- Nik 3249876509325615\n'- diduga berada di Bangkok\n'- no.telepon: 088964729102",  # noqa
             "Orang", "CDD-001", "Malang", "16 Oktober 1977", "Australia",
             "Pondok Indah Apartemen Tower 1 Blok A Lt 15 no. 1587, Jakarta Selatan"],  # noqa
            ["Alice Johnson Alias Alia John", "'- NIK nomor: 7654321098765432\n'- paspor nomor: C1234567\n'- pekerjaan: Dokter",  # noqa
             "Orang", "BDD-002", "Bandung", "12 Desember 1980", "Indonesia",
             "Jalan Cendana No.10, RT/RW. 004/005, Kel. Menteng, Kec. Menteng, Jakarta Pusat, DKI Jakarta"],  # noqa
            ["Bob Martin Alias Bobby", "'- NIK nomor: 2345678901234567\n'- paspor nomor: D2345678\n'- pekerjaan: Pengusaha",  # noqa
             "Orang", "ADD-003", "Yogyakarta", "23 Maret 1975", "Indonesia",
             "Kompleks Bukit Indah, Blok B3, No. 22, Sleman, Yogyakarta"],
            ["Charlie Brown Alias Charly", "'- NIK nomor: 3456789012345678\n'- paspor nomor: E3456789\n'- pekerjaan: Guru",  # noqa
             "Orang", "CDD-004", "Semarang", "15 April 1985", "Indonesia",
             "Perumahan Green Valley, Blok C2, No. 14, Semarang, Jawa Tengah"],
            ["David Williams Alias Dave", "'- NIK nomor: 4567890123456789\n'- paspor nomor: F4567890\n'- pekerjaan: Programmer",  # noqa
             "Orang", "DDD-005", "Jakarta", "30 Mei 1990", "Indonesia",
             "Apartemen Sudirman Park, Tower A, Lt. 12, No. 1203, Jakarta Pusat, DKI Jakarta"],  # noqa
            ["Eve Adams Alias Evie", "'- NIK nomor: 5678901234567890\n'- paspor nomor: G5678901\n'- pekerjaan: Seniman",  # noqa
             "Orang", "BDD-006", "Denpasar", "12 Juni 1988", "Indonesia",
             "Jalan Sunset Road No. 27, Kuta, Bali"],
            ["Frank Clark Alias Frankie", "'- NIK nomor: 6789012345678901\n'- paspor nomor: H6789012\n'- pekerjaan: Arsitek",  # noqa
             "Orang", "EDD-007", "Bandung", "14 Juli 1979", "Indonesia",
             "Perumahan Setiabudi, Blok D5, No. 18, Bandung, Jawa Barat"],
            ["Grace Lee Alias Gracie", "'- NIK nomor: 7890123456789012\n'- paspor nomor: I7890123\n'- pekerjaan: Peneliti",  # noqa
             "Orang", "ADD-008", "Surabaya", "25 Agustus 1984", "Indonesia",
             "Jalan Diponegoro No. 15, Surabaya, Jawa Timur"],
            ["Hank Thompson Alias Hanky", "'- NIK nomor: 8901234567890123\n'- paspor nomor: J8901234\n'- pekerjaan: Atlet",  # noqa
             "Orang", "DDD-009", "Medan", "2 September 1992", "Indonesia",
             "Perumahan Elite, Blok E1, No. 9, Medan, Sumatera Utara"],
            ["Ivy Green Alias Ivy", "'- NIK nomor: 9012345678901234\n'- paspor nomor: K9012345\n'- pekerjaan: Penyanyi",  # noqa
             "Orang", "BDD-010", "Palembang", "19 Oktober 1983", "Indonesia",
             "Jalan Merdeka No. 10, Palembang, Sumatera Selatan"],
            ["Jack Black Alias Jacky", "'- NIK nomor: 0123456789012345\n'- paspor nomor: L0123456\n'- pekerjaan: Pilot",  # noqa
             "Orang", "CDD-011", "Makassar", "30 November 1981", "Indonesia",
             "Kompleks Bandara, Blok F3, No. 2, Makassar, Sulawesi Selatan"],
            ["Karen White Alias Kary", "'- NIK nomor: 1234509876543210\n'- paspor nomor: M1234567\n'- pekerjaan: Chef",  # noqa
             "Orang", "ADD-012", "Manado", "5 Desember 1989", "Indonesia",
             "Jalan Sam Ratulangi No. 5, Manado, Sulawesi Utara"],
            ["Larry King Alias Larry", "'- NIK nomor: 2345678901234567\n'- paspor nomor: N2345678\n'- pekerjaan: Jurnalis",  # noqa
             "Orang", "DDD-013", "Balikpapan", "14 Januari 1974", "Indonesia",
             "Kompleks Pelabuhan, Blok G1, No. 3, Balikpapan, Kalimantan Timur"],  # noqa
            ["Mona Lisa Alias Mona", "'- NIK nomor: 3456789012345678\n'- paspor nomor: O3456789\n'- pekerjaan: Pelukis",  # noqa
             "Orang", "BDD-014", "Banjarmasin", "18 Februari 1987", "Indonesia",  # noqa
             "Jalan Ahmad Yani No. 8, Banjarmasin, Kalimantan Selatan"],
            ["Nick Fury Alias Nick", "'- NIK nomor: 4567890123456789\n'- paspor nomor: P4567890\n'- pekerjaan: Agen Rahasia",  # noqa
             "Orang", "EDD-015", "Pontianak", "24 Maret 1978", "Indonesia",
             "Jalan Gajah Mada No. 12, Pontianak, Kalimantan Barat"],
            ["Olivia Newton Alias Olivia", "'- NIK nomor: 5678901234567890\n'- paspor nomor: Q5678901\n'- pekerjaan: Aktris",  # noqa
             "Orang", "CDD-016", "Jayapura", "1 April 1991", "Indonesia",
             "Jalan Raya Sentani No. 3, Jayapura, Papua"],
            ["Paul Walker Alias Paul", "'- NIK nomor: 6789012345678901\n'- paspor nomor: R6789012\n'- pekerjaan: Aktor",  # noqa
             "Orang", "ADD-017", "Ambon", "6 Mei 1980", "Indonesia",
             "Jalan Pattimura No. 9, Ambon, Maluku"],
            ["Quincy Jones Alias Quincy", "'- NIK nomor: 7890123456789012\n'- paspor nomor: S7890123\n'- pekerjaan: Produser Musik",  # noqa
             "Orang", "DDD-018", "Kendari", "12 Juni 1985", "Indonesia",
             "Jalan Samudera No. 7, Kendari, Sulawesi Tenggara"],
            ["Rachel Green Alias Rachel", "'- NIK nomor: 8901234567890123\n'- paspor nomor: T8901234\n'- pekerjaan: Designer",  # noqa
             "Orang", "BDD-019", "Kupang", "22 Juli 1983", "Indonesia",
             "Jalan El Tari No. 11, Kupang, Nusa Tenggara Timur"]
        ]
        for row in data:
            ws.append(row)
        wb.save(output)
        output.seek(0)
        return SimpleUploadedFile(
            "test.xlsx",
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")  # noqa

    def upload_dttotdoc_and_process(self):
        """Upload and processing of a DTTOT Document
        and its saving into the dttotDoc model."""
        document_file = self.create_test_document_file()
        with self.settings(MEDIA_ROOT=self.test_media_path):
            response = self.client.post(
                self.document_url,
                {
                    'document_file': document_file,
                    'document_name': 'Test Document',
                    'document_type': 'DTTOT Document',
                    'document_file_type': 'XLSX'
                },
                format='multipart'
            )

            document_id = response.data['document']['document_id']


    def test_search_dttotDoc_by_name(self):
        response = self.client.get(
            reverse('dttotdocs:dttotdoc-search'), {'search': 'John'})
        self.assertEqual(
            response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_search_dttotDoc_by_nik(self):
        response = self.client.get(
            reverse('dttotdocs:dttotdoc-search'), {'search': '1234'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_search_dttotDoc_by_phone(self):
        response = self.client.get(
            reverse('dttotdocs:dttotdoc-search'), {'search': '0801'})
        self.assertEqual(
            response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            len(response.data), 2)