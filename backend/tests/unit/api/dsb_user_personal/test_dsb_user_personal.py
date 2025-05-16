from __future__ import annotations

from django.urls import reverse  #type: ignore # noqa: PGH003
from rest_framework import status  #type: ignore # noqa: PGH003
from rest_framework.authtoken.models import Token  #type: ignore # noqa: PGH003
from rest_framework.test import APITestCase  #type: ignore # noqa: PGH003

from app.dsb_user.dsb_user_personal.models import (
    DsbUserPersonal,  #type: ignore # noqa: PGH003
)
from app.user.models import User  #type: ignore # noqa: PGH003
from app.documents.models import Document  #type: ignore # noqa: PGH003

DSB_USER_PASSWORD_TEST = "t3Stp@ssw0rd"  # noqa: S105
DSB_USER_COUNT = 2

class DsbUserPersonalTests(APITestCase):

    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password=DSB_USER_PASSWORD_TEST,
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION="Token " + self.token.key)

        self.docuement = Document.objects.create(
            document_type="test",
            document_name="test",
            document_file_type="test",
        )

        self.dsb_user_personal = DsbUserPersonal.objects.create(
            document=self.docuement,
            personal_nik="1234567890123456",
            user_name="Test User",
        )

    def test_list_dsb_user_personal(self) -> None:
        url = reverse("dsb_user_personal:dsb-user-personal-list")

        self.client.force_authenticate(user=self.user)

        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK  #noqa: S101
        assert len(response.data) >= 1  #noqa: S101
