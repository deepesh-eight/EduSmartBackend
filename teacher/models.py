from django.db import models

from authentication.models import TeacherUser
# Create your models here.


class TeacherAttendence(models.Model):
    teacher = models.ForeignKey(TeacherUser, on_delete=models.CASCADE)
    date = models.DateField()
    mark_attendence = models.CharField(max_length=100)