# Generated by Django 5.0.4 on 2024-04-26 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('telegram_app', '0005_telegramgroup'),
    ]

    operations = [
        migrations.CreateModel(
            name='TelegramBot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('username', models.CharField(max_length=200)),
            ],
        ),
    ]
