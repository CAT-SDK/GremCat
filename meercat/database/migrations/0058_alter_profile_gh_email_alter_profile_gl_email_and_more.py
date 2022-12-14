# Generated by Django 4.0.4 on 2022-08-18 20:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0057_profile_remove_gitlabcredentials_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='gh_email',
            field=models.EmailField(blank=True, max_length=200, verbose_name='GitHub email'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gl_email',
            field=models.EmailField(blank=True, max_length=200, verbose_name='GitLab email'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='gl_username',
            field=models.CharField(blank=True, max_length=200, verbose_name='GitLab username'),
        ),
    ]
