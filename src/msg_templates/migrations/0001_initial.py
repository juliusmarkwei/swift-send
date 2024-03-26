# Generated by Django 5.0.3 on 2024-03-26 12:21

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contacts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_sent', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(db_column='created_by', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Template',
                'verbose_name_plural': 'Templates',
                'db_table': 'template',
                'unique_together': {('name', 'created_by')},
            },
        ),
        migrations.CreateModel(
            name='ContactTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('contact_id', models.ForeignKey(db_column='contact_id', on_delete=django.db.models.deletion.CASCADE, to='contacts.contact')),
                ('template_id', models.ForeignKey(db_column='template_id', on_delete=django.db.models.deletion.CASCADE, to='msg_templates.template')),
            ],
            options={
                'verbose_name': 'Contact Template',
                'verbose_name_plural': 'Contact Templates',
                'db_table': 'contact_template',
                'unique_together': {('contact_id', 'template_id')},
            },
        ),
    ]
