# Generated by Django 3.1 on 2025-03-19 10:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0070_consentpupil'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profile',
            name='auth_group',
        ),
    ]
