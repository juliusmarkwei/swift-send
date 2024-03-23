from django.contrib import admin
from .models import Contact

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'phone', 'email', 'created_by', 'created_at', 'updated_at')
    list_display_links = ('id', 'phone')
    search_fields = ('name', 'email')
    ordering = ('-created_at',)
    