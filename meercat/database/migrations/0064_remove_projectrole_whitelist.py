# Generated by Django 4.0.7 on 2022-12-23 17:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0063_alter_eventlog_event_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectrole',
            name='whitelist',
        ),
    ]