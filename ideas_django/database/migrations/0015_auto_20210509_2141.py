# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-05-09 21:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0014_auto_20210509_0112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='author',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
