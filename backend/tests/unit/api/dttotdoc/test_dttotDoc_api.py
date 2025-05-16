from __future__ import annotations  # noqa: N999

import io
import shutil
from pathlib import Path
from time import sleep
from typing import Any
from unittest.mock import patch

import pandas as pd  #type: ignore # noqa: PGH003
import pytest
from django.conf import settings  #type: ignore # noqa: PGH003
from django.contrib.auth import get_user_model  #type: ignore # noqa: PGH003
from django.core.files.uploadedfile import (  #type: ignore # noqa: PGH003
    SimpleUploadedFile,
)
from django.test import override_settings, TransactionTestCase  #type: ignore # noqa: PGH003
from django.urls import reverse  #type: ignore # noqa: PGH003
from openpyxl import Workbook  #type: ignore # noqa: PGH003
from rest_framework import status  #type: ignore # noqa: PGH003
from rest_framework.authtoken.models import Token  #type: ignore # noqa: PGH003
from rest_framework.test import APIClient, APITestCase  #type: ignore # noqa: PGH003
from unittest.mock import patch
from django.db import connection

User = get_user_model()

TEST_USER_PASSWORD = "Testp@ss!23"  # noqa: S105
EXPECTED_RESPONSE_LENGTH_2 = 2
EXPECTED_RESPONSE_LENGTH_3 = 3


@pytest.mark.django_db(transaction=True)
class DttotDocAPITestCase(APITestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = User.objects.create_user(
            email="test@example.com",
            username="testuser",
            password=TEST_USER_PASSWORD,
        )
        self.token, _ = Token.objects.get_or_create(user=self.user)
        self.client.force_authenticate(user=self.user)
        self.test_media_subdir = "test_media"
        self.test_media_path = Path(settings.MEDIA_ROOT) / self.test_media_subdir
        self.test_media_path.mkdir(parents=True, exist_ok=True)
        self.old_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = str(self.test_media_path)

    def tearDown(self):
        # Clean up test media
        shutil.rmtree(self.test_media_path, ignore_errors=True)
        settings.MEDIA_ROOT = self.old_media_root
        super().tearDown()

    @staticmethod
    def create_test_document_file():
        output = io.BytesIO()
        data = {
            "Nama": ["John Doe Alias Don John Alias John Krew"],
            "Deskripsi": [
                "'- NIK nomor: 1234567898765432\n'- paspor nomor: A0987654\n'- pekerjaan: Karyawan Swasta",
            ],
            "Terduga": ["Orang"],
            "Kode Densus": ["EDD-013"],
            "Tpt Lahir": ["Surabaya"],
            "Tgl Lahir": ["4 Januari 1973/4 November 1974/4 November 1973"],
            "WN": ["Indonesia"],
            "Alamat": [
                "Jalan Getis Gg.III/95A, RT/RW. 013/003, Kel. Lemah Putro, Kec. Sidoarjo, Kab/Kota. Sidoarjo, Prov. Jawa Timur",
            ],
        }
        df = pd.DataFrame(data)
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return SimpleUploadedFile(
            "test.xlsx",
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def test_create_and_update_dttotdoc(self):
        """Test full lifecycle: upload, retrieve, update DTTOT docs."""
        # Upload
        document_file = self.create_test_document_file()
        upload_response = self.client.post(
            reverse("documents:document-list"),
            {
                "document_file": document_file,
                "document_name": "Test Document",
                "document_type": "DTTOT Report",
                "document_file_type": "XLSX",
            },
            format="multipart",
        )
        # Assert upload success
        assert (  #noqa: S101
            upload_response.status_code == status.HTTP_201_CREATED
        ), "Document upload failed"

        # Extract document_id
        response_data = upload_response.json()
        assert response_data, "Empty upload response"
        document_id = response_data.get("document_id")
        assert document_id, "No document_id in upload response"

        # Poll for DTTOT docs
        dttot_docs = None
        list_url = f"{reverse('DttotDoc:dttot-doc-list')}?identifier={document_id}"
        for _ in range(30):
            resp = self.client.get(list_url)
            assert resp.status_code == status.HTTP_200_OK
            data = resp.json()
            if data:
                dttot_docs = data
                break
            sleep(1)
        assert dttot_docs, "dttotDoc was not found in the response"

        # Validate first DTTOT doc fields
        doc_item = dttot_docs[0]
        assert doc_item["document"] == document_id
        for key in ("dttot_id", "document_data", "updated_at", "user"):
            assert key in doc_item, f"{key} missing in doc_item"

        # Update the DTTOT doc
        detail_url = reverse(
            "dttotdocs:dttot-doc-detail",
            kwargs={"dttot_id": doc_item["dttot_id"]}
        )
        update_payload = {
            "dttot_type": "Updated Type",
            "dttot_first_name": "FirstUp",
            "dttot_last_name": "LastUp",
            "dttot_domicile_address": "Updated Address",
            "dttot_description_1": "Updated Description",
        }
        update_resp = self.client.patch(detail_url, update_payload, format="json")
        assert update_resp.status_code == status.HTTP_200_OK

        # Confirm update persisted
        final_data = self.client.get(detail_url).json()
        assert final_data.get("dttot_type") == "Updated Type"
        assert final_data.get("dttot_first_name") == "FirstUp"
        assert final_data.get("dttot_last_name") == "LastUp"


class DttotDocReportTestCase(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.user = User.objects.create_user(
            "newuser",
            "newuser@example.com",
            TEST_USER_PASSWORD,
        )
        cls.document_url = reverse("document-create")

    def setUp(self) -> None:
        self.client.force_authenticate(user=self.user)

        self.test_media_subdir = "test_media"
        self.test_media_path = Path(settings.MEDIA_ROOT) / self.test_media_subdir
        self.test_media_path.mkdir(parents=True, exist_ok=True)

        self.old_media_root = settings.MEDIA_ROOT
        settings.MEDIA_ROOT = str(self.test_media_path)

    def tearDown(self) -> None:
        settings.MEDIA_ROOT = self.old_media_root
        shutil.rmtree(self.test_media_path, ignore_errors=True)
        super().tearDown()

    @staticmethod
    def create_test_document_file() -> SimpleUploadedFile:
        output = io.BytesIO()
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append(
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
        data = [
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
            [
                "Jane Mary alias Maria Yan Alias Yan Smith",
                "'- Nomor Paspor: B 0897455\n'- tanggal 5 agustus 2011 menuju Malaysia\n'- Nik 3249876509325615\n'- diduga berada di Bangkok\n'- no.telepon: 088964729102",
                "Orang",
                "CDD-001",
                "Malang",
                "16 Oktober 1977",
                "Australia",
                "Pondok Indah Apartemen Tower 1 Blok A Lt 15 no. 1587, Jakarta Selatan",
            ],
            [
                "Alice Johnson Alias Alia John",
                "'- NIK nomor: 7654321098765432\n'- paspor nomor: C1234567\n'- pekerjaan: Dokter",
                "Orang",
                "BDD-002",
                "Bandung",
                "12 Desember 1980",
                "Indonesia",
                "Jalan Cendana No.10, RT/RW. 004/005, Kel. Menteng, Kec. Menteng, Jakarta Pusat, DKI Jakarta",
            ],
            [
                "Bob Martin Alias Bobby",
                "'- NIK nomor: 2345678901234567\n'- paspor nomor: D2345678\n'- pekerjaan: Pengusaha",
                "Orang",
                "ADD-003",
                "Yogyakarta",
                "23 Maret 1975",
                "Indonesia",
                "Kompleks Bukit Indah, Blok B3, No. 22, Sleman, Yogyakarta",
            ],
            [
                "Charlie Brown Alias Charly",
                "'- NIK nomor: 3456789012345678\n'- paspor nomor: E3456789\n'- pekerjaan: Guru",
                "Orang",
                "CDD-004",
                "Semarang",
                "15 April 1985",
                "Indonesia",
                "Perumahan Green Valley, Blok C2, No. 14, Semarang, Jawa Tengah",
            ],
            [
                "David Williams Alias Dave",
                "'- NIK nomor: 4567890123456789\n'- paspor nomor: F4567890\n'- pekerjaan: Programmer",
                "Orang",
                "DDD-005",
                "Jakarta",
                "30 Mei 1990",
                "Indonesia",
                "Apartemen Sudirman Park, Tower A, Lt. 12, No. 1203, Jakarta Pusat, DKI Jakarta",
            ],
            [
                "Eve Adams Alias Evie",
                "'- NIK nomor: 5678901234567890\n'- paspor nomor: G5678901\n'- pekerjaan: Seniman",
                "Orang",
                "BDD-006",
                "Denpasar",
                "12 Juni 1988",
                "Indonesia",
                "Jalan Sunset Road No. 27, Kuta, Bali",
            ],
            [
                "Frank Clark Alias Frankie",
                "'- NIK nomor: 6789012345678901\n'- paspor nomor: H6789012\n'- pekerjaan: Arsitek",
                "Orang",
                "EDD-007",
                "Bandung",
                "14 Juli 1979",
                "Indonesia",
                "Perumahan Setiabudi, Blok D5, No. 18, Bandung, Jawa Barat",
            ],
            [
                "Grace Lee Alias Gracie",
                "'- NIK nomor: 7890123456789012\n'- paspor nomor: I7890123\n'- pekerjaan: Peneliti",
                "Orang",
                "ADD-008",
                "Surabaya",
                "25 Agustus 1984",
                "Indonesia",
                "Jalan Diponegoro No. 15, Surabaya, Jawa Timur",
            ],
            [
                "Hank Thompson Alias Hanky",
                "'- NIK nomor: 8901234567890123\n'- paspor nomor: J8901234\n'- pekerjaan: Atlet",
                "Orang",
                "DDD-009",
                "Medan",
                "2 September 1992",
                "Indonesia",
                "Perumahan Elite, Blok E1, No. 9, Medan, Sumatera Utara",
            ],
            [
                "Ivy Green Alias Ivy",
                "'- NIK nomor: 9012345678901234\n'- paspor nomor: K9012345\n'- pekerjaan: Penyanyi",
                "Orang",
                "BDD-010",
                "Palembang",
                "19 Oktober 1983",
                "Indonesia",
                "Jalan Merdeka No. 10, Palembang, Sumatera Selatan",
            ],
            [
                "Jack Black Alias Jacky",
                "'- NIK nomor: 0123456789012345\n'- paspor nomor: L0123456\n'- pekerjaan: Pilot",
                "Orang",
                "CDD-011",
                "Makassar",
                "30 November 1981",
                "Indonesia",
                "Kompleks Bandara, Blok F3, No. 2, Makassar, Sulawesi Selatan",
            ],
            [
                "Karen White Alias Kary",
                "'- NIK nomor: 1234509876543210\n'- paspor nomor: M1234567\n'- pekerjaan: Chef",
                "Orang",
                "ADD-012",
                "Manado",
                "5 Desember 1989",
                "Indonesia",
                "Jalan Sam Ratulangi No. 5, Manado, Sulawesi Utara",
            ],
            [
                "Larry King Alias Larry",
                "'- NIK nomor: 2345678901234567\n'- paspor nomor: N2345678\n'- pekerjaan: Jurnalis",
                "Orang",
                "DDD-013",
                "Balikpapan",
                "14 Januari 1974",
                "Indonesia",
                "Kompleks Pelabuhan, Blok G1, No. 3, Balikpapan, Kalimantan Timur",
            ],
            [
                "Mona Lisa Alias Mona",
                "'- NIK nomor: 3456789012345678\n'- paspor nomor: O3456789\n'- pekerjaan: Pelukis",
                "Orang",
                "BDD-014",
                "Banjarmasin",
                "18 Februari 1987",
                "Indonesia",
                "Jalan Ahmad Yani No. 8, Banjarmasin, Kalimantan Selatan",
            ],
            [
                "Nick Fury Alias Nick",
                "'- NIK nomor: 4567890123456789\n'- paspor nomor: P4567890\n'- pekerjaan: Agen Rahasia",
                "Orang",
                "EDD-015",
                "Pontianak",
                "24 Maret 1978",
                "Indonesia",
                "Jalan Gajah Mada No. 12, Pontianak, Kalimantan Barat",
            ],
            [
                "Olivia Newton Alias Olivia",
                "'- NIK nomor: 5678901234567890\n'- paspor nomor: Q5678901\n'- pekerjaan: Aktris",
                "Orang",
                "CDD-016",
                "Jayapura",
                "1 April 1991",
                "Indonesia",
                "Jalan Raya Sentani No. 3, Jayapura, Papua",
            ],
            [
                "Paul Walker Alias Paul",
                "'- NIK nomor: 6789012345678901\n'- paspor nomor: R6789012\n'- pekerjaan: Aktor",
                "Orang",
                "ADD-017",
                "Ambon",
                "6 Mei 1980",
                "Indonesia",
                "Jalan Pattimura No. 9, Ambon, Maluku",
            ],
            [
                "Quincy Jones Alias Quincy",
                "'- NIK nomor: 7890123456789012\n'- paspor nomor: S7890123\n'- pekerjaan: Produser Musik",
                "Orang",
                "DDD-018",
                "Kendari",
                "12 Juni 1985",
                "Indonesia",
                "Jalan Samudera No. 7, Kendari, Sulawesi Tenggara",
            ],
            [
                "Rachel Green Alias Rachel",
                "'- NIK nomor: 8901234567890123\n'- paspor nomor: T8901234\n'- pekerjaan: Designer",
                "Orang",
                "BDD-019",
                "Kupang",
                "22 Juli 1983",
                "Indonesia",
                "Jalan El Tari No. 11, Kupang, Nusa Tenggara Timur",
            ],
        ]
        for row in data:
            worksheet.append(row)
        workbook.save(output)
        output.seek(0)
        return SimpleUploadedFile(
            "test.xlsx",
            output.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    def upload_dttotdoc_and_process(self) -> None:
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

            document_id = response.data["document"]["document_id"]

    def test_search_dttotdoc_by_name(self) -> None:
        response = self.client.get(
            reverse("dttotdocs:dttotdoc-search"),
            {"search": "John"},
        )
        assert response.status_code == status.HTTP_200_OK  # noqa: S101
        assert len(response.data) == EXPECTED_RESPONSE_LENGTH_2  # noqa: S101

    def test_search_dttotdoc_by_nik(self) -> None:
        response = self.client.get(
            reverse("dttotdocs:dttotdoc-search"),
            {"search": "1234"},
        )
        assert response.status_code == status.HTTP_200_OK  # noqa: S101
        assert len(response.data) == EXPECTED_RESPONSE_LENGTH_3  # noqa: S101

    def test_search_dttotdoc_by_phone(self) -> None:
        response = self.client.get(
            reverse("dttotdocs:dttotdoc-search"),
            {"search": "0801"},
        )
        assert response.status_code == status.HTTP_200_OK  # noqa: S101
        assert len(response.data) == EXPECTED_RESPONSE_LENGTH_2  # noqa: S101
