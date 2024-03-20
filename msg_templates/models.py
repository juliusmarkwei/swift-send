from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Template(models.Model):
    name = models.CharField(max_length=255)
    message_content = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Template'
        verbose_name_plural = 'Templates'
        db_table = 'template'