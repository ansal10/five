# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-04-27 10:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fiveapp', '0011_auto_20170421_0905'),
    ]

    operations = [
        migrations.AddField(
            model_name='users',
            name='active',
            field=models.BooleanField(default=True),
        ),
    ]
