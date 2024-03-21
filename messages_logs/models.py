from django.db import models
from contacts.models import Contact
from django.contrib.auth import get_user_model
from msg_templates.models import Template

User = get_user_model()

class MessageLog(models.Model):   
    content = models.TextField(max_length=255)
    sent_by = models.ForeignKey(User, on_delete=models.CASCADE, db_column='created_by')
    sent_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20)
    
    def __str__(self):
        return self.id
    
    class Meta:
        verbose_name = 'Message Log'
        verbose_name_plural = 'Message Logs'
        db_table = 'message log'
        
        
class ReceipientLog(models.Model):
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, db_column='receipient')
    message = models.ForeignKey(MessageLog, on_delete=models.CASCADE, db_column='message')
    
    def __str__(self):
        return self.contact
    
    class Meta:
        verbose_name = 'Receipient Log'
        verbose_name_plural = 'Receipient Logs'
        db_table = 'receipient log'
        
