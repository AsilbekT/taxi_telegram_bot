# Generated by Django 5.0.4 on 2024-05-01 16:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_app', '0014_ridepost_last_ride_message_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ridepost',
            name='last_ride_message_id',
        ),
    ]
