from django.contrib import admin
from .models import UserAccount

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'phone', 'created_at')
    list_display_links = ('id', 'username')
    search_fields = ('username',)
    ordering = ('-created_at',)
    