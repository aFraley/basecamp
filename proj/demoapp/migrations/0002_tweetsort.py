# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-08 17:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('demoapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TweetSort',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('twt_date', models.DateTimeField()),
                ('twt_count', models.CharField(max_length=200)),
            ],
        ),
    ]
