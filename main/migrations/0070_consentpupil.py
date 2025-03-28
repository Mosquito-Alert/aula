# Generated by Django 3.1 on 2025-03-18 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0069_merge_20250318_1511'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsentPupil',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('n', models.IntegerField()),
                ('consent', models.BooleanField(default=False)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_consent', to='main.profile')),
            ],
        ),
    ]
