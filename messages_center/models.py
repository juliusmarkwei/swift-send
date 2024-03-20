from django.db import models
from contacts.models import Contact
from msg_templates.models import Template

class Message(models.Model):
    message_status = (
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    )
    
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE)
    message_content = models.TextField(max_length=255)
    sent_to = models.CharField(max_length=255)
    template = models.ForeignKey(Template, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=message_status, default='pending', max_length=10)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.message
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        db_table = 'message'