from django.contrib import admin
from .models import UserAccount

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'full_name', 'phone', 'created_at', 'updated_at')
    list_display_links = ('username',)
    search_fields = ('username',)
    ordering = ('-created_at',)
    