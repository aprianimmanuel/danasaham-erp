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