# Generated by Django 3.2.7 on 2022-03-06 01:27

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('readmore_app', '0012_readinglogbook_userext_user_reading_log'),
    ]

    operations = [
        migrations.AddField(
            model_name='readinglogbook',
            name='time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
