# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2016-12-19 00:44
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whayp', '0002_post_pub_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='photo',
            name='full_file_url',
        ),
        migrations.AlterField(
            model_name='post',
            name='pub_date',
            field=models.DateTimeField(default=datetime.datetime(2016, 12, 19, 2, 44, 13, 920698)),
        ),
    ]
