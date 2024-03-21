from django.contrib import admin
from .models import MessageLog, ReceipientLog

@admin.register(MessageLog)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'status', 'sent_by', 'sent_at', 'status')
    search_fields = ('content',)
    ordering = ('-sent_at',)
    

@admin.register(ReceipientLog)
class ReceipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact', 'message')
    search_fields = ('contact',)
    ordering = ('-id',)