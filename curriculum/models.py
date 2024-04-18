from django.db import models

# Create your models here.


class Curriculum(models.Model):
    school_id = models.CharField(max_length=255, null=True, blank=True)
    academic_session = models.CharField()
    exam_board = models.CharField(max_length=255, null=True, blank=True)
    subject_name_code = models.JSONField(default=list)
    class_name = models.CharField(max_length=255, null=True, blank=True)
    section = models.CharField(max_length=255,null=True, blank=True)
    curriculum_name = models.TextField()

    def __str__(self):
        return f"{self.id}"


class CurriculumPDF(models.Model):
    curriculum = models.OneToOneField(Curriculum, on_delete=models.CASCADE)
    curriculum_pdf_file = models.FileField(upload_to='')