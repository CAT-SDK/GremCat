# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2021-05-09 01:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0013_auto_20210302_1648'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('body', models.TextField()),
            ],
            options={
                'verbose_name': 'comment',
                'verbose_name_plural': 'comments',
                'db_table': 'comment',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='CommitTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sha', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name': 'commit tag',
                'verbose_name_plural': 'commit tags',
                'db_table': 'commit_tag',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('updated_at', models.DateTimeField()),
                ('closed_at', models.DateTimeField()),
                ('locked', models.BooleanField()),
                ('url', models.CharField(max_length=256)),
                ('number', models.IntegerField()),
                ('state', models.CharField(max_length=64)),
            ],
            options={
                'verbose_name': 'issue',
                'verbose_name_plural': 'commits',
                'db_table': 'issue',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='IssueAssignee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'issue has assignee',
                'verbose_name_plural': 'issue has assignees',
                'db_table': 'issue_has_assignee',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='IssueComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Comment')),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Issue')),
            ],
            options={
                'verbose_name': 'issue has comment',
                'verbose_name_plural': 'issue has comments',
                'db_table': 'issue_has_comment',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='IssueLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Issue')),
            ],
            options={
                'verbose_name': 'issue has label',
                'verbose_name_plural': 'issue has labels',
                'db_table': 'issue_has_label',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': 'label',
                'verbose_name_plural': 'labels',
                'db_table': 'label',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='Milestone',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=64)),
                ('description', models.TextField()),
                ('title', models.CharField(max_length=256)),
                ('due_on', models.DateTimeField()),
                ('created_at', models.DateTimeField()),
                ('updated_at', models.DateTimeField()),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Issue')),
            ],
            options={
                'verbose_name': 'milestone',
                'db_table': 'milestone',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PullRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=256)),
                ('description', models.TextField()),
                ('updated_at', models.DateTimeField()),
                ('locked', models.BooleanField()),
                ('url', models.CharField(max_length=256)),
                ('number', models.IntegerField()),
                ('state', models.CharField(max_length=64)),
                ('head_sha', models.CharField(max_length=256)),
            ],
            options={
                'verbose_name': 'pull request',
                'verbose_name_plural': 'pull requests',
                'db_table': 'pr',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PullRequestAssignee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name': 'pr has assignee',
                'verbose_name_plural': 'pr has assignees',
                'db_table': 'pr_has_assignee',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PullRequestComment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Comment')),
                ('pr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.PullRequest')),
            ],
            options={
                'verbose_name': 'pr has comment',
                'verbose_name_plural': 'pr has comments',
                'db_table': 'pr_has_comment',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PullRequestCommit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('commit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.CommitTag')),
                ('pr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.PullRequest')),
            ],
            options={
                'verbose_name': 'pr has commit',
                'verbose_name_plural': 'pr has commits',
                'db_table': 'pr_has_commit',
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='PullRequestLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Label')),
                ('pr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.PullRequest')),
            ],
            options={
                'verbose_name': 'pr has label',
                'verbose_name_plural': 'pr has labels',
                'db_table': 'pr_has_label',
                'ordering': ['id'],
            },
        ),
        migrations.AddField(
            model_name='author',
            name='name',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AddField(
            model_name='author',
            name='url',
            field=models.CharField(max_length=256, null=True),
        ),
        migrations.AlterModelTable(
            name='personauthor',
            table='person_has_author',
        ),
        migrations.AddField(
            model_name='pullrequestassignee',
            name='assignee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Author'),
        ),
        migrations.AddField(
            model_name='pullrequestassignee',
            name='pr',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.PullRequest'),
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='assignees',
            field=models.ManyToManyField(related_name='pr_assignee', through='database.PullRequestAssignee', to='database.Author'),
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pr_author', to='database.Author'),
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='comments',
            field=models.ManyToManyField(through='database.PullRequestComment', to='database.Comment'),
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='commits',
            field=models.ManyToManyField(through='database.PullRequestCommit', to='database.CommitTag'),
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='labels',
            field=models.ManyToManyField(through='database.PullRequestLabel', to='database.Label'),
        ),
        migrations.AddField(
            model_name='pullrequest',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Project'),
        ),
        migrations.AddField(
            model_name='issuelabel',
            name='label',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Label'),
        ),
        migrations.AddField(
            model_name='issueassignee',
            name='assignee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Author'),
        ),
        migrations.AddField(
            model_name='issueassignee',
            name='issue',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Issue'),
        ),
        migrations.AddField(
            model_name='issue',
            name='assignees',
            field=models.ManyToManyField(related_name='issue_assignee', through='database.IssueAssignee', to='database.Author'),
        ),
        migrations.AddField(
            model_name='issue',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issue_author', to='database.Author'),
        ),
        migrations.AddField(
            model_name='issue',
            name='comments',
            field=models.ManyToManyField(through='database.IssueComment', to='database.Comment'),
        ),
        migrations.AddField(
            model_name='issue',
            name='labels',
            field=models.ManyToManyField(through='database.IssueLabel', to='database.Label'),
        ),
        migrations.AddField(
            model_name='issue',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Project'),
        ),
        migrations.AddField(
            model_name='comment',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='database.Author'),
        ),
    ]
