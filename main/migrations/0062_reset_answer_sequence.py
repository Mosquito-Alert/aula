# Generated by Django 3.1 on 2024-01-22 08:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0061_auto_20240111_1527'),
    ]

    operations = [
        migrations.RunSQL(
            "SELECT setval('main_answer_id_seq', (select max(id)+1 from main_answer), true);"
        )
    ]