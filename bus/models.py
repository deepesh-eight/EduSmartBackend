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


class Route(models.Model):
    school_id = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Stop(models.Model):
    route = models.ForeignKey(Route, related_name='stops', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    time = models.TimeField()

    class Meta:
        unique_together = ('route', 'name', 'time')

    def __str__(self):
        return f"{self.name} at {self.time.strftime('%H:%M')}"
