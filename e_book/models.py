from django.db import models

# Create your models here.


class Ebook(models.Model):
    book = models.FileField(upload_to='')
    book_name = models.CharField(max_length=255)
    writer_name = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255)
    suporting_detail = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    curriculum = models.ForeignKey('curriculum.Curriculum', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Evideos(models.Model):
    video = models.FileField(upload_to='')
    book_name = models.CharField(max_length=255)
    writer_name = models.CharField(max_length=255)
    class_name = models.CharField(max_length=255)
    suporting_detail = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    curriculum = models.ForeignKey('curriculum.Curriculum', on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)