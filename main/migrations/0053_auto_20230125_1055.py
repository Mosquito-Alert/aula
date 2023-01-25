# Generated by Django 3.1 on 2023-01-25 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0052_quizcorrection'),
    ]

    operations = [
        migrations.AddField(
            model_name='quizcorrection',
            name='comments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='quizcorrection',
            name='correction_value',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
