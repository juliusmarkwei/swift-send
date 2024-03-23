from django.test import TestCase
from django.contrib.auth import get_user_model
from src.contacts.models import Contact
from src.message_logs.models import MessageLog, RecipientLog

User = get_user_model()

class RecipientLogModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test_user', password='test_password', email='test@mail.com')

    def setUp(self):
        self.message_log = MessageLog.objects.create(content='Test message content', author=self.user)
        self.contact = Contact.objects.create(phone='123456789', created_by=self.user)

    def test_recipient_log_creation(self):
        recipient_log = RecipientLog.objects.create(contact=self.contact, message=self.message_log)

        self.assertIsNotNone(recipient_log)
        self.assertEqual(recipient_log.contact, self.contact)
        self.assertEqual(recipient_log.message, self.message_log)

    def test_recipient_log_str_representation(self):
        recipient_log = RecipientLog.objects.create(contact=self.contact, message=self.message_log)

        self.assertEqual(str(recipient_log), str(self.contact.id))

    
    def test_recipient_log_deletion_with_null_contact(self):
        recipient_log = RecipientLog.objects.create(contact=None, message=self.message_log)

        self.assertTrue(RecipientLog.objects.filter(pk=recipient_log.pk).exists())

        if recipient_log.contact:
            recipient_log.contact.delete()
        
        self.assertTrue(RecipientLog.objects.filter(pk=recipient_log.pk).exists())

