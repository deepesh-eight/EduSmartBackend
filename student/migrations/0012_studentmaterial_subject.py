# Generated by Django 4.2.10 on 2024-05-05 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('student', '0011_remove_studentmaterial_subject_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentmaterial',
            name='subject',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]