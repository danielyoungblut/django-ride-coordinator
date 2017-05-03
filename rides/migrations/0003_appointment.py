# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-03-04 18:21
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0002_yalie_is_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('desired_time', models.DateTimeField()),
                ('available_start', models.DateTimeField()),
                ('available_end', models.DateTimeField()),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
