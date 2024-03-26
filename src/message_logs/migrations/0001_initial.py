# Generated by Django 5.0.3 on 2024-03-24 17:02

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
            name='MessageLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField(max_length=255)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('author_id', models.ForeignKey(db_column='author_id', on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Message Log',
                'verbose_name_plural': 'Message Logs',
                'db_table': 'message_log',
            },
        ),
        migrations.CreateModel(
            name='RecipientLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(default='PENDING', max_length=100)),
                ('contact_id', models.ForeignKey(db_column='receipient', null=True, on_delete=django.db.models.deletion.SET_NULL, to='contacts.contact')),
                ('message_id', models.ForeignKey(db_column='message_id', on_delete=django.db.models.deletion.CASCADE, to='message_logs.messagelog')),
            ],
            options={
                'verbose_name': 'Recipient Log',
                'verbose_name_plural': 'Recipient Logs',
                'db_table': 'recipient_log',
            },
        ),
    ]
