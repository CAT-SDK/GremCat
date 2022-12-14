# Generated by Django 4.0.4 on 2022-07-20 17:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('database', '0049_alter_project_id_gitlabcredentials'),
    ]

    operations = [
        migrations.CreateModel(
            name='EventLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uri', models.CharField(blank=True, max_length=500)),
                ('view_name', models.CharField(blank=True, max_length=200)),
                ('view_args', models.CharField(blank=True, max_length=200)),
                ('view_kwargs', models.CharField(blank=True, max_length=400)),
                ('datetime', models.DateTimeField()),
                ('event_type', models.CharField(choices=[('FEAT', 'Feature used'), ('ERR', 'Error'), ('NOTIFICATION', 'Notification sent'), ('NOTIFICATION_FAIL', 'Failed to send notification')], max_length=25)),
                ('log', models.TextField(blank=True)),
                ('user', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
