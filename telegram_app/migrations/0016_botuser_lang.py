# Generated by Django 5.0.4 on 2024-05-10 14:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_app', '0015_remove_ridepost_last_ride_message_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='botuser',
            name='lang',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
