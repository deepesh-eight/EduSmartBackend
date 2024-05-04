from django.db import models

# Create your models here.


class Classes(models.Model):
    school_id = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255)


class Subjects(models.Model):
    school_id = models.CharField(max_length=255)
    subject_name = models.CharField(max_length=255)


class Curriculum(models.Model):
    school_id = models.CharField(max_length=255, null=True, blank=True)
    curriculum_name = models.CharField(max_length=255)
    select_class = models.ForeignKey(Classes, on_delete=models.CASCADE)
    primary_subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name="admin_curriculum_primary_subject")
    optional_subject = models.ForeignKey(Subjects, on_delete=models.CASCADE, related_name="admin_curriculum_optional_subject", blank=True, null=True)
    syllabus = models.FileField(upload_to='syllabus/', null=True, blank=True)
    discription = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f"{self.id}"


class CurriculumPDF(models.Model):
    curriculum = models.OneToOneField(Curriculum, on_delete=models.CASCADE)
    curriculum_pdf_file = models.FileField(upload_to='')