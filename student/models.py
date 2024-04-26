from django.db import models

from authentication.models import StudentUser


# Create your models here.


class StudentAttendence(models.Model):
    student = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    date = models.DateField()
    mark_attendence = models.CharField(max_length=100)


class ExmaReportCard(models.Model):
    school_id = models.CharField(max_length=255)
    class_name = models.CharField(max_length=200)
    class_section = models.CharField(max_length=200)
    student_name = models.CharField(max_length=200)
    roll_no = models.CharField(max_length=200)
    exam_type = models.CharField(max_length=200)
    exam_month = models.DateField()
    marks_grades = models.JSONField()
    total_marks = models.CharField(max_length=200)
    overall_grades = models.CharField(max_length=200)
    status = models.CharField(max_length=200, default=0)