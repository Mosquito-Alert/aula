# Generated by Django 3.1 on 2024-10-02 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0064_auto_20240208_1438'),
    ]

    operations = [
        migrations.CreateModel(
            name='CenterMapData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=500)),
                ('lat', models.FloatField()),
                ('lon', models.FloatField()),
                ('year', models.IntegerField()),
                ('participation_years', models.CharField(max_length=100, null=True)),
                ('hashtag', models.CharField(max_length=100)),
                ('n_pupils', models.IntegerField(default=0)),
                ('n_groups', models.IntegerField(default=0)),
                ('n_bs_total', models.IntegerField(default=0)),
                ('n_storm_drain_water', models.IntegerField(default=0)),
                ('n_storm_drain_dry', models.IntegerField(default=0)),
                ('no_other_bs', models.IntegerField(default=0)),
                ('has_awards', models.BooleanField(default=False)),
            ],
        ),
    ]
