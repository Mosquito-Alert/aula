# Generated by Django 3.1 on 2024-02-08 14:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0063_reset_question_sequence'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='type',
            field=models.IntegerField(choices=[(0, 'Test'), (1, 'Material'), (2, 'Enquesta'), (3, 'Pujar fitxer'), (4, 'Enquesta professorat'), (5, 'Resposta oberta'), (6, 'Resposta oberta professorat')]),
        ),
    ]
