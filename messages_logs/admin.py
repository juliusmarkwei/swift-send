from django.contrib import admin
from .models import MessageLog, RecipientLog

@admin.register(MessageLog)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'status', 'author', 'sent_at', 'status')
    search_fields = ('content',)
    ordering = ('-sent_at',)
    

@admin.register(RecipientLog)
class ReceipientAdmin(admin.ModelAdmin):
    list_display = ('id', 'contact', 'message')
    search_fields = ('contact',)
    ordering = ('-id',)