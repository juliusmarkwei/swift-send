from django.test import TestCase
from django.contrib.auth import get_user_model
from src.contacts.models import Contact
from src.msg_templates.models import Template, ContactTemplate

User = get_user_model()

class ContactTemplateModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a test user for the contacts' and templates' creators
        cls.user = User.objects.create_user(username='test_user', password='test_password', email='test@mail.com')

    def setUp(self):
        # Create test contacts
        self.contact1 = Contact.objects.create(phone='1234567890', created_by=self.user)
        self.contact2 = Contact.objects.create(phone='9876543210', created_by=self.user)

        # Create test templates
        self.template1 = Template.objects.create(name='Template 1', content='Template 1 content', created_by=self.user)
        self.template2 = Template.objects.create(name='Template 2', content='Template 2 content', created_by=self.user)

        # Create test contact templates
        self.contact_template1 = ContactTemplate.objects.create(contact=self.contact1, template=self.template1)
        self.contact_template2 = ContactTemplate.objects.create(contact=self.contact2, template=self.template2)

    def test_contact_template_creation(self):
        # Test whether contact templates were created successfully
        self.assertEqual(ContactTemplate.objects.count(), 2)

    def test_contact_template_deletion(self):
        # Delete a contact template
        self.contact_template1.delete()

        # Verify that the contact template is no longer present
        self.assertFalse(ContactTemplate.objects.filter(pk=self.contact_template1.pk).exists())

    def test_contact_template_str_method(self):
        # Test the __str__ method of the contact template
        self.assertEqual(str(self.contact_template1), f"{self.contact1.pk} - {self.template1.name}")
