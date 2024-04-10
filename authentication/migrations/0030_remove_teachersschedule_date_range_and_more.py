# Generated by Django 4.2.10 on 2024-04-10 10:37

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0029_rename_end_date_teachersschedule_date_range_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teachersschedule',
            name='date_range',
        ),
        migrations.AddField(
            model_name='teachersschedule',
            name='end_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AddField(
            model_name='teachersschedule',
            name='start_date',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
