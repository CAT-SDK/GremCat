# Generated by Django 4.0.4 on 2022-08-18 20:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('database', '0056_alter_projectrole_project_alter_projectrole_user_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gh_login', models.CharField(max_length=200, verbose_name='GitHub login')),
                ('gh_email', models.EmailField(max_length=200, verbose_name='GitHub email')),
                ('gl_username', models.CharField(max_length=200, verbose_name='GitLab username')),
                ('gl_email', models.EmailField(max_length=200, verbose_name='GitLab email')),
                ('subscriptions', models.JSONField(blank=True, default=dict)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Profile',
            },
        ),
        migrations.RemoveField(
            model_name='gitlabcredentials',
            name='user',
        ),
        migrations.RemoveField(
            model_name='subscriptions',
            name='user',
        ),
        migrations.DeleteModel(
            name='GitHubCredentials',
        ),
        migrations.DeleteModel(
            name='GitLabCredentials',
        ),
        migrations.DeleteModel(
            name='Subscriptions',
        ),
    ]