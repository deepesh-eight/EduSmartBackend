# Generated by Django 4.2.10 on 2024-07-04 10:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('management', '0002_salaryformat'),
    ]

    operations = [
        migrations.AddField(
            model_name='salaryformat',
            name='field_amount',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=16),
        ),
    ]