# Generated by Django 4.0.4 on 2022-06-03 17:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0038_projectrole_user_alter_projectrole_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectrole',
            name='project',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='members', to='database.project'),
            preserve_default=False,
        ),
    ]
