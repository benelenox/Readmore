# Generated by Django 3.2.7 on 2022-02-03 19:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('readmore_app', '0004_auto_20220129_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notification',
            name='notification_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
