# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-11 00:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demoapp', '0003_auto_20160709_1755'),
    ]

    operations = [
        migrations.CreateModel(
            name='TweetCount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('twt_id', models.CharField(max_length=50)),
            ],
        ),
    ]
