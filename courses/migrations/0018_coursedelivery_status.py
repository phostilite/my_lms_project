# Generated by Django 5.0.6 on 2024-07-10 07:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0017_scormcloudcourse_registration_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='coursedelivery',
            name='status',
            field=models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=20),
        ),
    ]
