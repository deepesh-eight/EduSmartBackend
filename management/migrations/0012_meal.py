# Generated by Django 4.2.10 on 2024-09-17 05:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0011_remove_salary_joining_date_salary_salary_month'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meal_type', models.IntegerField(choices=[(1, 'Breakfast'), (2, 'Lunch'), (3, 'Snacks')])),
                ('date', models.DateField()),
                ('items', models.JSONField()),
                ('status', models.BooleanField(default=True)),
            ],
        ),
    ]
