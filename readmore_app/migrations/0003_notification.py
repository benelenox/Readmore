# Generated by Django 3.2.7 on 2022-01-28 20:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('readmore_app', '0002_userext_user_friends'),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('notification_id', models.AutoField(primary_key=True, serialize=False)),
                ('notification_title', models.CharField(max_length=10000)),
                ('notification_time', models.DateTimeField()),
                ('notification_link', models.CharField(blank=True, max_length=10000)),
                ('notification_link_text', models.CharField(blank=True, max_length=10000)),
                ('notification_message', models.TextField()),
                ('notification_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='readmore_app.userext')),
            ],
        ),
    ]
