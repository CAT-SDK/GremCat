# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-02-25 07:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0011_auto_20210225_0752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='commit',
            name='branch',
            field=models.TextField(),
        ),
    ]