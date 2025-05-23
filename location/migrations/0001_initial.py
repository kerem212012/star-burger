# Generated by Django 5.2 on 2025-05-15 17:04

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(db_index=True, max_length=200, unique=True, verbose_name='Адрес')),
                ('lat', models.FloatField(blank=True, null=True, verbose_name='Широта')),
                ('lon', models.FloatField(blank=True, null=True, verbose_name='Долгота')),
                ('query_data', models.DateField(db_index=True, default=django.utils.timezone.now, verbose_name='Дата запроса')),
            ],
            options={
                'verbose_name': 'Локация',
                'verbose_name_plural': 'Локация',
            },
        ),
    ]
