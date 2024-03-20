from django.db import models
from contacts.models import Contact
from django.contrib.auth import get_user_model
from msg_templates.models import Template

User = get_user_model()

class Message(models.Model):
    message_status = (
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )
    
    message_content = models.TextField(max_length=255)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, db_column='created_by')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=message_status, default='pending', max_length=10)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.message
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        db_table = 'message'
        

class ContactMessage(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.contact
    
    class Meta:
        verbose_name = 'Contact Message'
        verbose_name_plural = 'Contact Messages'
        db_table = 'contact_message'
        unique_together = ('contact', 'message')
        