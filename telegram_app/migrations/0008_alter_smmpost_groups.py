# Generated by Django 5.0.4 on 2024-04-26 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_app', '0007_smmpost_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='smmpost',
            name='groups',
            field=models.ManyToManyField(to='telegram_app.telegramgroup'),
        ),
    ]
