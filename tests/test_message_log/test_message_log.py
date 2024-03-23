from django.test import TestCase
from django.contrib.auth import get_user_model
from src.message_logs.models import MessageLog

User = get_user_model()

class MessageLogModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test_user', password='test_password', email='test@mail.com')

    def test_message_log_creation(self):
        message_log = MessageLog.objects.create(
            content='Test message content',
            author=self.user
        )
        self.assertIsNotNone(message_log)
        self.assertEqual(message_log.content, 'Test message content')
        self.assertEqual(message_log.author, self.user)

    def test_str_representation(self):
        message_log = MessageLog.objects.create(
            content='Test message content',
            author=self.user
        )
        self.assertEqual(str(message_log), str(message_log.id))
