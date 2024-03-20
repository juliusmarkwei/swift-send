from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'message_content', 'status', 'created_at', 'updated_at')
    search_fields = ('message_content',)
    ordering = ('-created_at',)