# Generated by Django 3.2.7 on 2022-04-26 23:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('readmore_app', '0022_auto_20220422_1937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='post_user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='readmore_app.userext'),
        ),
    ]