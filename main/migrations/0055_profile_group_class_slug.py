# Generated by Django 3.1 on 2023-01-30 08:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0054_profile_group_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='group_class_slug',
            field=models.CharField(max_length=500, null=True),
        ),
    ]
