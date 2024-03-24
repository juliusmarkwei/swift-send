from django.db import models
from src.contacts.models import Contact
from django.contrib.auth import get_user_model
from src.msg_templates.models import Template

User = get_user_model()

class MessageLog(models.Model):   
    content = models.TextField(max_length=255)
    author_id = models.ForeignKey(User, on_delete=models.PROTECT, db_column='author_id')
    sent_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name = 'Message Log'
        verbose_name_plural = 'Message Logs'
        db_table = 'message_log'
        
    
class RecipientLog(models.Model):   
    contact_id = models.ForeignKey(Contact, on_delete=models.SET_NULL, null=True, db_column='receipient')
    message_id = models.ForeignKey(MessageLog, on_delete=models.CASCADE, db_column='message_id')
    status = models.CharField(max_length=20, default='PENDING')
    
    def __str__(self):
        return str(self.contact_id)
    
    class Meta:
        verbose_name = 'Recipient Log'
        verbose_name_plural = 'Recipient Logs'
        db_table = 'recipient_log'
        
