from django.db import models

from authentication.models import StudentUser


# Create your models here.


class StudentAttendence(models.Model):
    student = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    date = models.DateField()
    mark_attendence = models.CharField(max_length=100)