# Generated by Django 3.1 on 2020-11-05 07:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20201104_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='group_password',
            field=models.CharField(default='abcd', max_length=4, verbose_name='Password grup'),
            preserve_default=False,
        ),
    ]