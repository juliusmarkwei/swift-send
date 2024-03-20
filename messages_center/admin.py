from django.contrib import admin
from .models import Message

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact', 'message_content', 'template', 'created_at')
    list_display_links = ('id', 'contact')
    search_fields = ('contact',)
    ordering = ('-created_at',)