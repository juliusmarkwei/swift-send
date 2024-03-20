from django.contrib import admin
from .models import Contact, UserContact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone', 'email', 'created_at')
    list_display_links = ('id', 'phone')
    search_fields = ('name', 'email')
    ordering = ('-created_at',)
    
    
@admin.register(UserContact)
class UserContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'contact', 'created_at')
    list_display_links = ('id', 'user')
    search_fields = ('user', 'contact')
    ordering = ('-created_at',)