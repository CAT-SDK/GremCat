# Generated by Django 4.0.4 on 2022-07-28 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0054_alter_eventlog_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eventlog',
            name='event_type',
            field=models.CharField(choices=[('DEBUGGING', 'Debugging log'), ('FEAT', 'Feature used'), ('ERR', 'Error'), ('NOTIFICATION', 'Notification sent'), ('NO_NOTIFICATION', 'No notification sent'), ('NOTIFICATION_FAIL', 'Failed to send notification')], max_length=25),
        ),
    ]
