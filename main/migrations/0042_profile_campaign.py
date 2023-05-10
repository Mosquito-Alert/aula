# Generated by Django 3.1 on 2022-02-24 11:25

from django.db import migrations, models
import django.db.models.deletion
import main.models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_auto_20220224_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='campaign',
            field=models.ForeignKey(blank=True, default=main.models.get_current_active_campaign(), null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profiles', to='main.campaign'),
        ),
    ]
