from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from authentication.models import StaffUser

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
    
class Bus(models.Model):
    school_id = models.CharField(max_length=255, null=True, blank=True)
    bus_image = models.ImageField(upload_to='buses/', blank=True)
    bus_number = models.CharField(max_length=20, unique=True)
    driver_name = models.ForeignKey(StaffUser, related_name='driver', on_delete=models.CASCADE)
    operator_name = models.ForeignKey(StaffUser, related_name='operator',on_delete=models.CASCADE, blank=True, null=True)
    bus_route = models.ForeignKey(Route, related_name='bus_route',on_delete=models.CASCADE, blank=True, null=True)
    alternate_route = models.ForeignKey(Route, related_name='alternate_bus_route',on_delete=models.CASCADE, blank=True, null=True)
    bus_capacity = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.bus_number
