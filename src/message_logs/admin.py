from django.contrib import admin
from .models import MessageLog, RecipientLog

@admin.register(MessageLog)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'author_id', 'sent_at')
    search_fields = ('content',)
    ordering = ('-sent_at',)
    

@admin.register(RecipientLog)
class ReceipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact_id', 'message_id', 'status')
    search_fields = ('contact',)
    ordering = ('-id',)