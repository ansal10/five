# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-03 12:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fiveapp', '0002_auto_20170403_1018'),
    ]

    operations = [
        migrations.CreateModel(
            name='Opentok',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.CharField(max_length=31)),
                ('api_key', models.CharField(max_length=255)),
                ('api_secret', models.CharField(max_length=255)),
            ],
        ),
    ]
