# Generated by Django 4.2.10 on 2024-06-22 07:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0069_staffuser_experience_staffuser_highest_qualification'),
        ('student', '0021_alter_connectwithteacher_end_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentmaterial',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authentication.teacheruser'),
        ),
    ]
