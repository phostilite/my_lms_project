# Generated by Django 5.0.6 on 2024-06-30 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0004_alter_scormcloudcourse_created_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='scormcloudcourse',
            name='created_at',
            field=models.DateTimeField(),
        ),
        migrations.AlterField(
            model_name='scormcloudcourse',
            name='updated_at',
            field=models.DateTimeField(),
        ),
    ]
