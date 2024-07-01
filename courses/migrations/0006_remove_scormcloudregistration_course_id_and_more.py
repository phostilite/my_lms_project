# Generated by Django 5.0.6 on 2024-06-30 19:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0005_alter_scormcloudcourse_created_at_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='scormcloudregistration',
            name='course_id',
        ),
        migrations.AddField(
            model_name='scormcloudregistration',
            name='course',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='courses.scormcloudcourse'),
        ),
    ]
