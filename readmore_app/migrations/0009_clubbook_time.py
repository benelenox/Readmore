# Generated by Django 3.2 on 2022-02-20 20:30

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('readmore_app', '0008_auto_20220218_1323'),
    ]

    operations = [
        migrations.AddField(
            model_name='clubbook',
            name='time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]