# Generated by Django 4.0.2 on 2022-03-07 18:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('readmore_app', '0014_comment'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProfilePost',
            fields=[
                ('post_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='readmore_app.post')),
                ('post_profile_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='readmore_app.userext')),
            ],
            bases=('readmore_app.post',),
        ),
    ]
