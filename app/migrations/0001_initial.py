# Generated by Django 3.2.23 on 2023-12-20 01:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('fcm_django', '0011_fcmdevice_fcm_django_registration_id_user_id_idx'),
    ]

    operations = [
        migrations.CreateModel(
            name='Thread',
            fields=[
                ('thread_id', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('device', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='fcm_django.fcmdevice')),
                ('threads', models.ManyToManyField(blank=True, to='app.Thread')),
            ],
        ),
    ]
