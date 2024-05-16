from django.db import models

# Create your models here.


class Classes(models.Model):
    school_id = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255)


class Curriculum(models.Model):
    school_id = models.CharField(max_length=255, null=True, blank=True)
    curriculum_name = models.CharField(max_length=255)
    select_class = models.CharField(max_length=255, blank=True, null=True)
    syllabus = models.FileField(upload_to='syllabus/', null=True, blank=True)
    discription = models.TextField(null=True, blank=True)
    curriculum_type = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.id}"


class Subjects(models.Model):
    curriculum_id = models.ForeignKey(Curriculum, on_delete=models.CASCADE, blank=True, null=True)
    primary_subject = models.CharField(max_length=255, blank=True, null=True)
    optional_subject = models.CharField(max_length=255, blank=True, null=True)


class CurriculumPDF(models.Model):
    curriculum = models.OneToOneField(Curriculum, on_delete=models.CASCADE)
    curriculum_pdf_file = models.FileField(upload_to='')