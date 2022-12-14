# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-08-16 23:30
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0022_issuetag_pullrequestissue'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('api_id', models.IntegerField()),
                ('type', models.CharField(max_length=128)),
                ('public', models.BooleanField()),
                ('created_at', models.DateTimeField()),
            ],
            options={
                'verbose_name': 'event',
                'verbose_name_plural': 'events',
                'db_table': 'event',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='EventActor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actor_id', models.IntegerField()),
                ('name', models.CharField(max_length=128)),
                ('url', models.URLField()),
            ],
            options={
                'verbose_name': 'event actor',
                'verbose_name_plural': 'event actors',
                'db_table': 'event_actor',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='EventOrg',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('org_id', models.IntegerField()),
                ('login', models.CharField(max_length=128)),
                ('gravatar_id', models.CharField(max_length=128)),
                ('avatar_url', models.URLField()),
                ('url', models.URLField()),
            ],
            options={
                'verbose_name': 'event org',
                'verbose_name_plural': 'event orgs',
                'db_table': 'event_org',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='EventPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('title', models.CharField(max_length=128)),
                ('action', models.CharField(max_length=128)),
                ('sha', models.CharField(max_length=128)),
                ('url', models.URLField()),
            ],
            options={
                'verbose_name': 'event page',
                'verbose_name_plural': 'event pages',
                'db_table': 'event_page',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='EventPages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.EventPage')),
            ],
            options={
                'verbose_name': 'event has page',
                'verbose_name_plural': 'event has pages',
                'db_table': 'event_has_page',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='EventPayload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=128)),
                ('ref', models.CharField(max_length=128, null=True)),
                ('ref_type', models.CharField(max_length=128, null=True)),
                ('master_branch', models.CharField(max_length=128, null=True)),
                ('description', models.CharField(max_length=1024, null=True)),
                ('forkee_url', models.URLField(null=True)),
                ('issue_url', models.URLField(null=True)),
                ('comment_url', models.URLField(null=True)),
                ('member_login', models.CharField(max_length=128, null=True)),
                ('pr_number', models.IntegerField(null=True)),
                ('pr_url', models.URLField(null=True)),
                ('pr_review_url', models.URLField(null=True)),
                ('push_id', models.IntegerField(null=True)),
                ('size', models.IntegerField(null=True)),
                ('distinct_size', models.IntegerField(null=True)),
                ('head', models.CharField(max_length=128, null=True)),
                ('before', models.CharField(max_length=128, null=True)),
                ('release_url', models.URLField(null=True)),
                ('effective_date', models.CharField(max_length=128, null=True)),
                ('comment', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='database.Comment')),
            ],
            options={
                'verbose_name': 'event payload',
                'verbose_name_plural': 'event payloads',
                'db_table': 'event_payload',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='EventRepo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('repo_id', models.IntegerField()),
                ('login', models.CharField(max_length=128)),
                ('gravatar_id', models.CharField(max_length=128)),
                ('avatar_url', models.URLField()),
                ('url', models.URLField()),
            ],
            options={
                'verbose_name': 'event repo',
                'verbose_name_plural': 'event repos',
                'db_table': 'event_repo',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='eventpages',
            name='event_payload',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.EventPayload'),
        ),
        migrations.AddField(
            model_name='event',
            name='actor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.EventActor'),
        ),
        migrations.AddField(
            model_name='event',
            name='org',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.EventOrg'),
        ),
        migrations.AddField(
            model_name='event',
            name='payload',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='database.EventPayload'),
        ),
        migrations.AddField(
            model_name='event',
            name='repo',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.EventRepo'),
        ),
    ]
