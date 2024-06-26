from django.contrib import admin
from .models import Template, ContactTemplate


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'created_at', 'last_sent', 'updated_at')


@admin.register(ContactTemplate)
class ContactTemplateAdmin(admin.ModelAdmin):
    list_display = ('contact_id', 'template_id', 'created_at')