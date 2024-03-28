# Generated by Django 4.2.10 on 2024-03-28 06:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0010_errorlogging'),
    ]

    operations = [
        migrations.RenameField(
            model_name='teacheruser',
            old_name='salary',
            new_name='ctc',
        ),
        migrations.RenameField(
            model_name='teacheruser',
            old_name='first_name',
            new_name='full_name',
        ),
        migrations.RemoveField(
            model_name='teacheruser',
            name='last_name',
        ),
        migrations.AddField(
            model_name='teacheruser',
            name='address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='teacheruser',
            name='experience',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='teacheruser',
            name='role',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='teacheruser',
            name='section',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='teacheruser',
            name='subject',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name='teacheruser',
            name='class_taught',
        ),
        migrations.AddField(
            model_name='teacheruser',
            name='class_taught',
            field=models.TextField(blank=True, null=True),
        ),
    ]
