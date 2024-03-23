from django.test import TestCase
from django.contrib.auth import get_user_model
from src.msg_templates.models import Template

User = get_user_model()

class TemplateModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='test_user', password='test_password', email='test@mail.com')
        
        # Create a template object for testing
        cls.template = Template.objects.create(name="Test Template", content="Test Content", created_by=User.objects.create(username="testuser"))

    def test_template_creation(self):
        template = Template.objects.create(name='Test Template', content='Test template content', created_by=self.user)

        self.assertIsNotNone(template)
        self.assertEqual(template.name, 'Test Template')
        self.assertEqual(template.content, 'Test template content')
        self.assertEqual(template.created_by, self.user)

    def test_template_str_representation(self):
        template = Template.objects.create(name='Test Template', content='Test template content', created_by=self.user)
        self.assertEqual(str(template), 'Test Template')

    def test_template_deletion(self):
        template = Template.objects.create(name='Test Template', content='Test template content', created_by=self.user)
        
        template.delete()

        self.assertFalse(Template.objects.filter(id=template.id).exists())

    def test_template_modification(self):
        template = Template.objects.create(name='Test Template', content='Test template content', created_by=self.user)
        
        template.name = 'Modified Template'
        template.content = 'Modified template content'
        template.save()

        # Retrieve the modified template from the database
        modified_template = Template.objects.get(id=template.id)

        # Verify that the modifications were saved correctly
        self.assertEqual(modified_template.name, 'Modified Template')
        self.assertEqual(modified_template.content, 'Modified template content')

    def test_template_reading(self):
        # Retrieve the template using its ID
        retrieved_template = Template.objects.get(id=self.template.id)

        # Verify that the retrieved template matches the original template
        self.assertEqual(retrieved_template.name, self.template.name)
        self.assertEqual(retrieved_template.content, self.template.content)