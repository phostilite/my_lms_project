# Generated by Django 5.0.6 on 2024-06-30 10:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_scormcloudregistration'),
    ]

    operations = [
        migrations.AddField(
            model_name='scormcloudcourse',
            name='category',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='scormcloudcourse',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='course_covers/'),
        ),
        migrations.AddField(
            model_name='scormcloudcourse',
            name='duration',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scormcloudcourse',
            name='long_description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='scormcloudcourse',
            name='price',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=8, null=True),
        ),
        migrations.AddField(
            model_name='scormcloudcourse',
            name='short_description',
            field=models.CharField(blank=True, max_length=500, null=True),
        ),
    ]
