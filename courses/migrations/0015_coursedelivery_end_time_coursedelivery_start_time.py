# Generated by Django 5.0.6 on 2024-07-09 22:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0014_alter_coursedelivery_deactivation_date_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursedelivery',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='coursedelivery',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
    ]
