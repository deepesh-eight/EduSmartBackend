# Generated by Django 4.2.10 on 2024-09-16 09:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0009_salary_leave_days_salary_master_days_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salaryformat',
            name='salary_structure',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='salary_formats', to='management.salary'),
        ),
    ]
