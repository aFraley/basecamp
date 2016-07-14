# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-06 00:09
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tweet_id', models.CharField(max_length=50, unique=True)),
                ('tweet_date', models.DateTimeField()),
                ('tweet_source', models.TextField()),
                ('tweet_favorite_cnt', models.CharField(max_length=50)),
                ('tweet_retweet_cnt', models.CharField(max_length=50)),
                ('tweet_text', models.TextField()),
            ],
        ),
    ]