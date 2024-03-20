# Generated by Django 5.0.3 on 2024-03-20 02:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=255)),
                ('last_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('middle_name', models.CharField(blank=True, default='', max_length=255, null=True)),
                ('email', models.EmailField(blank=True, max_length=100, null=True, unique=True)),
                ('phone', models.CharField(max_length=20)),
                ('info', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
