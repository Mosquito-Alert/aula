# Generated by Django 3.1 on 2021-10-07 08:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_auto_20210930_0630'),
    ]

    operations = [
        migrations.AddField(
            model_name='educationcenter',
            name='hashtag',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
    ]