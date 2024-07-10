# Generated by Django 5.0.6 on 2024-07-09 19:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0010_coursedelivery'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('is_present', models.BooleanField(default=False)),
                ('course_delivery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.coursedelivery')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'course_delivery', 'date')},
            },
        ),
        migrations.CreateModel(
            name='Enrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('enrollment_date', models.DateTimeField(auto_now_add=True)),
                ('completion_date', models.DateTimeField(blank=True, null=True)),
                ('is_completed', models.BooleanField(default=False)),
                ('course_delivery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.coursedelivery')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'course_delivery')},
            },
        ),
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField()),
                ('comments', models.TextField()),
                ('submission_date', models.DateTimeField(auto_now_add=True)),
                ('course_delivery', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='courses.coursedelivery')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'course_delivery')},
            },
        ),
    ]