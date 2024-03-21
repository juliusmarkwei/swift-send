from django.db import models
from contacts.models import Contact
from django.contrib.auth import get_user_model

User = get_user_model()

class Template(models.Model):
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
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return str(self.contact.pk) + ' - ' + self.template.name
    
    class Meta:
        verbose_name = 'Contact Template'
        verbose_name_plural = 'Contact Templates'
        db_table = 'contact_template'
        unique_together = ('contact', 'template')