# Generated by Django 4.2.10 on 2024-04-12 09:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0031_teachersschedule_teacher'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teachersschedule',
            name='teacher',
        ),
    ]