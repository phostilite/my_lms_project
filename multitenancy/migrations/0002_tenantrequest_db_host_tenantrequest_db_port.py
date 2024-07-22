# Generated by Django 5.0.6 on 2024-07-22 08:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('multitenancy', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tenantrequest',
            name='db_host',
            field=models.CharField(default='localhost', max_length=255),
        ),
        migrations.AddField(
            model_name='tenantrequest',
            name='db_port',
            field=models.IntegerField(default=5432),
        ),
    ]
