# Generated by Django 5.0.4 on 2024-04-26 14:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_app', '0008_alter_smmpost_groups'),
    ]

    operations = [
        migrations.CreateModel(
            name='Road',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('road_name', models.CharField(max_length=200)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='telegram_app.telegramgroup')),
            ],
        ),
    ]
