from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Contact(models.Model):
    first_name = models.CharField(max_length=255, default='', blank=True, null=True)
    last_name = models.CharField(max_length=255, default='', blank=True, null=True)
    middle_name = models.CharField(max_length=255, default='', blank=True, null=True)
    email = models.EmailField(max_length=100, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=20)
    info = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, db_column='created_by')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name
    
    class Meta:
        verbose_name = 'Contact'
        verbose_name_plural = 'Contacts'
        db_table = 'contact'
        unique_together = ('phone', 'created_by')
    