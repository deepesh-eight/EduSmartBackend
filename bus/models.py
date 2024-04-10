from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class Bus(models.Model):
    bus_image = models.ImageField(upload_to='', blank=True)
    bus_number = models.CharField(max_length=20, unique=True)
    driver_name = models.CharField(max_length=100)
    driver_gender = models.CharField(max_length=10)
    driver_phone_no = PhoneNumberField(blank=True, null=True)
    operator_name = models.CharField(max_length=100)
    operator_gender = models.CharField(max_length=10)
    operator_email = models.EmailField()
    operator_phone_no = PhoneNumberField(blank=True, null=True)
    bus_start_timing = models.TimeField()
    bus_start_from_school = models.TimeField()

    def __str__(self):
        return self.bus_number

    def get_driver_phone_no_without_country_code(self):
        if not self.driver_phone_no:
            return None
        return str(self.driver_phone_no.as_national.lstrip('0').strip().replace(' ', ''))

    def get_operator_phone_no_without_country_code(self):
        if not self.operator_phone_no:
            return None
        return str(self.operator_phone_no.as_national.lstrip('0').strip().replace(' ', ''))


class BusRoute(models.Model):
    bus = models.ForeignKey(Bus,on_delete=models.CASCADE)
    route_name = models.CharField(max_length=100)
    primary_start_time = models.TimeField()
    primary_start_stop = models.CharField(max_length=100)
    primary_next_stop = models.JSONField(null=True)
    alternate_start_time = models.TimeField(null=True, blank=True)
    alternate_next_stop = models.JSONField(null=True, blank=True)

    def __str__(self):
        return self.route_name
