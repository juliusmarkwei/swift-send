from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_jwt.settings import api_settings

User = get_user_model()

class ContactViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='test_user', password='password', email='test@mail.com')
        payload = api_settings.JWT_PAYLOAD_HANDLER(self.user)
        self.token = api_settings.JWT_ENCODE_HANDLER(payload)

    def test_get_authenticated(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.token}')
        response = self.client.get('/api/contacts')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_unauthenticated(self):
        response = self.client.get('/api/contacts')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_filter_contacts_by_phone(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.token}')
        response = self.client.get('/api/contacts?phone=1234567890')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_contacts_by_first_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.token}')
        response = self.client.get('/api/contacts?first_name=John')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_filter_contacts_by_last_name(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'JWT {self.token}')
        response = self.client.get('/api/contacts?last_name=Doe')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        