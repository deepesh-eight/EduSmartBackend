# Generated by Django 4.2.10 on 2024-04-10 09:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0028_eventscalender'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teachersschedule',
            old_name='end_date',
            new_name='date_range',
        ),
        migrations.RemoveField(
            model_name='teachersschedule',
            name='start_date',
        ),
    ]
