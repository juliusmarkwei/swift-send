from django.test import TestCase
from django.contrib.auth import get_user_model
from src.contacts.models import Contact

User = get_user_model()

class TestContactModel(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test_user', email='test@example.com', password='password')

    def setUp(self):
        self.contact = Contact.objects.create(
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone='1234567890',
            info='Test contact',
            created_by=self.user
        )

    def test_contact_str_representation(self):
        self.assertEqual(str(self.contact), str(self.contact.id))

    def test_contact_creation(self):
        contact_count = Contact.objects.count()
        self.assertEqual(contact_count, 1)

    def test_contact_fields(self):
        self.assertEqual(self.contact.first_name, 'John')
        self.assertEqual(self.contact.last_name, 'Doe')
        self.assertEqual(self.contact.email, 'john@example.com')
        self.assertEqual(self.contact.phone, '1234567890')
        self.assertEqual(self.contact.info, 'Test contact')
        self.assertEqual(self.contact.created_by, self.user)

    def test_contact_verbose_names(self):
        self.assertEqual(Contact._meta.verbose_name, 'Contact')
        self.assertEqual(Contact._meta.verbose_name_plural, 'Contacts')

    def test_contact_unique_together_constraint(self):
        duplicate_contact = Contact(
            first_name='Jane',
            last_name='Doe',
            email='jane@example.com',
            phone='1234567890',
            info='Duplicate contact',
            created_by=self.user
        )
        with self.assertRaises(Exception):
            duplicate_contact.save()

    def test_contact_created_at_and_updated_at(self):
        self.assertIsNotNone(self.contact.created_at)
        self.assertIsNotNone(self.contact.updated_at)
        self.assertLessEqual(self.contact.created_at, self.contact.updated_at)

