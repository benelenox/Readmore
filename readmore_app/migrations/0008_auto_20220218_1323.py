# Generated by Django 3.2.7 on 2022-02-18 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('readmore_app', '0007_chat_chat_type'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClubBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('isbn', models.CharField(max_length=20)),
            ],
        ),
        migrations.AlterField(
            model_name='club',
            name='club_library',
            field=models.ManyToManyField(related_name='clubs', to='readmore_app.ClubBook'),
        ),
    ]
