from __future__ import annotations

from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase

from app.config.core.models import User, dsb_user_personal

DSB_USER_PASSWORD_TEST = "t3Stp@ssw0rd"  #noqa: S106
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

        self.dsb_user_personal = dsb_user_personal.objects.create(
            user_id=self.user.user_id,
            personal_nik="1234567890123456",
            user_name="Test User",
        )

    def test_list_dsb_user_personal(self) -> None:
        url = reverse("dsb_user_personal:dsb-user-personal-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK  #noqa: S101
        assert len(response.data) >= 1  #noqa: S101

    def test_create_dsb_user_personal(self) -> None:
        url = reverse("dsb_user_personal:dsb-user-personal-list")
        data = {
            "user": self.user.user_id,
            "personal_nik": "2345678901234567",
            "user_name": "New Test User",
        }
        response = self.client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED  #noqa: S101
        assert dsb_user_personal.objects.count() == DSB_USER_COUNT  # noqa: S101
        assert dsb_user_personal.objects.get(personal_nik="2345678901234567").user_name == "New Test User"  #noqa: S101

    def test_retrieve_dsb_user_personal(self) -> None:
        url = reverse(
            "dsb_user_personal:dsb-user-personal-details",
            args=[self.dsb_user_personal.dsb_user_personal_id],
        )
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK  #noqa: S101
        assert response.data["personal_nik"] == self.dsb_user_personal.personal_nik  #noqa: S101

    def test_update_dsb_user_personal(self) -> None:
        url = reverse(
            "dsb_user_personal:dsb-user-personal-details",
            args=[self.dsb_user_personal.dsb_user_personal_id],
        )
        data = {
            "user_id": self.user.user_id,
            "personal_nik": "1234567890123456",
            "user_name": "Updated Test User",
        }
        response = self.client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK  #noqa: S101
        self.dsb_user_personal.refresh_from_db()
        assert self.dsb_user_personal.user_name == "Updated Test User"  #noqa: S101

    def test_partial_update_dsb_user_personal(self) -> None:
        url = reverse(
            "dsb_user_personal:dsb-user-personal-details",
            args=[self.dsb_user_personal.dsb_user_personal_id],
        )
        data = {"user_name": "Partially Updated Test User"}
        response = self.client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK  #noqa: S101
        self.dsb_user_personal.refresh_from_db()
        assert self.dsb_user_personal.user_name == "Partially Updated Test User"  #noqa: S101

    def test_delete_dsb_user_personal(self) -> None:
        url = reverse(
            "dsb_user_personal:dsb-user-personal-details",
            args=[self.dsb_user_personal.dsb_user_personal_id],
        )
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT  #noqa: S101
        assert dsb_user_personal.objects.count() == 0  #noqa: S101
