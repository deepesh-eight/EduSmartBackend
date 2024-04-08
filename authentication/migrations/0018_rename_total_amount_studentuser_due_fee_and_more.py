# Generated by Django 4.2.10 on 2024-04-04 06:18

import datetime
from django.db import migrations, models
import django.db.models.deletion
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('curriculum', '0001_initial'),
        ('authentication', '0017_remove_teacheruser_certificate_certificate'),
    ]

    operations = [
        migrations.RenameField(
            model_name='studentuser',
            old_name='total_amount',
            new_name='due_fee',
        ),
        migrations.AddField(
            model_name='studentuser',
            name='bus_number',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studentuser',
            name='bus_route',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studentuser',
            name='curriculum',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='curriculum.curriculum'),
        ),
        migrations.AddField(
            model_name='studentuser',
            name='father_phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
        migrations.AddField(
            model_name='studentuser',
            name='mother_occupation',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='studentuser',
            name='mother_phone_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, region=None),
        ),
        migrations.AddField(
            model_name='studentuser',
            name='name',
            field=models.CharField(default=1, max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studentuser',
            name='permanent_address',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='studentuser',
            name='section',
            field=models.CharField(default=1, max_length=50),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='studentuser',
            name='total_fee',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='class',
            name='class_name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='studentuser',
            name='admission_date',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='studentuser',
            name='blood_group',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='studentuser',
            name='class_enrolled',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='studentuser',
            name='dob',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='studentuser',
            name='father_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='studentuser',
            name='gender',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='studentuser',
            name='mother_name',
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
        migrations.AlterField(
            model_name='studentuser',
            name='religion',
            field=models.CharField(max_length=100),
        ),
    ]