# Generated by Django 4.2.10 on 2024-09-18 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0082_remove_teacheruser_fcm_token_user_fcm_token'),
    ]

    operations = [
        migrations.AddField(
            model_name='teacheruser',
            name='fcm_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
