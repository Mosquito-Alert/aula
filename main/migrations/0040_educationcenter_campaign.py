# Generated by Django 3.1 on 2022-02-24 11:11

from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_campaign'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationcenter',
            name='campaign',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.campaign'),
        ),
    ]
