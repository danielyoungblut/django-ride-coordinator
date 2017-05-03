# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-10 16:18
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0005_appointment_pickup'),
    ]

    operations = [
        migrations.CreateModel(
            name='RideRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='current_people',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='appointment',
            name='max_people',
            field=models.IntegerField(default=3),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='riderequest',
            name='appointment',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ride_request', to='rides.Appointment'),
        ),
        migrations.AddField(
            model_name='riderequest',
            name='creator',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ride_creator', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='riderequest',
            name='requester',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ride_requester', to=settings.AUTH_USER_MODEL),
        ),
    ]
