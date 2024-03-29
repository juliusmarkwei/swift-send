from django.db import models
from src.contacts.models import Contact
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Template(models.Model):
    id = models.UUIDField(default=uuid.uuid4, unique=True, primary_key=True, editable=False)
    name = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, db_column='created_by')
    created_at = models.DateTimeField(auto_now_add=True)
    last_sent = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    
    class Meta:
        verbose_name = 'Template'
        verbose_name_plural = 'Templates'
        db_table = 'template'
        unique_together = ('name', 'created_by')
        
        
class ContactTemplate(models.Model):
    contact_id = models.ForeignKey(Contact, on_delete=models.CASCADE, db_column='contact_id')
    template_id = models.ForeignKey(Template, on_delete=models.CASCADE, db_column='template_id')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.contact_id.full_name) + ' - ' + self.template_id.name
    
    class Meta:
        verbose_name = 'Contact Template'
        verbose_name_plural = 'Contact Templates'
        db_table = 'contact_template'
        unique_together = ('contact_id', 'template_id')