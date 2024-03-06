from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from core.models import dttotDoc


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

        # Create a sample dttotDoc
        self.sample_dttotDoc = dttotDoc.objects.create(
            input_by=self.user,
            dttot_type="Personal",
            _dttot_first_name="Encryptedfirst",
            _dttot_last_name="Encryptedsecond",
            _dttot_domicile_address1="Jalan in aja dulu",
            _dttot_description_1="digoyang bosquwh"
        )

    def test_create_dttotDoc(self):
        url = reverse('dttotdoc-list')
        data = {
            'dttot_type': 'New Type',
            '_dttot_first_name': 'EncryptedNewFirst',
            '_dttot_last_name': 'EncryptedNewSecond',
            '_dttot_domicile_address1': 'jalan sepanjang kenangan',
            '_dttot_description_1': 'terlalu digoyang nih bosquwh'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            dttotDoc.objects.count(), 2
        )
        self.assertEqual(
            dttotDoc.objects.get(
                document_id=response.data['dttot_id']
            ).dttot_type, 'New Type'
        )

    def test_retrieve_dttotDoc(self):
        url = reverse(
            'dttotdoc-detail',
            args=[self.sample.dttotDoc.dttot_id]
        )
        response = self.client.get(url)
        self.assertEqual(
            response.status_code, status.HTTP_200_OK
        )
        self.assertEqual(
            response.data['dttot_type'],
            self.sample_dttotDoc.dttot_type
        )

    def test_update_dttotDoc(self):
        url = reverse(
            'dttotdoc-detail',
            args=[self.sample_dttotDoc.dttot_id]
        )
        updated_data = {
            'dttot_type': 'Corporate',
            '_dttot_work_number': '0987654321',
            '_dttot_description_2': 'namanya juga usaha kan?',
        }
        response = self.client.patch(
            url,
            updated_data,
            format='json'
        )
        self.sample_dttotDoc.refresh_from_db()
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            self.sample_dttotDoc.dttot_type,
            'Updated Type'
        )

    def test_delete_dttotDoc(self):
        url = reverse(
            'dttotdoc-detail',
            args=[self.sample_dttotDoc.dttot_id]
        )
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(dttotDoc.objects.count(), 0)
