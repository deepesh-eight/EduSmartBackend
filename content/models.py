from django.db import models
from curriculum.models import Curriculum, Subjects, Classes
from constants import CONTENT_TYPES

class Content(models.Model):
    school_id = models.CharField(max_length=255, null=True, blank=True)
    content_media = models.FileField(upload_to='content/', blank=True, null=True)
    content_media_link = models.URLField(max_length=1024, blank=True, null=True)
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPES)
    content_name = models.CharField(max_length=255)
    content_creator = models.CharField(max_length=255, blank=True, null=True)
    curriculum = models.ForeignKey(Curriculum, on_delete=models.SET_NULL, null=True, blank=True)
    classes = models.ForeignKey(Classes, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.ForeignKey(Subjects, on_delete=models.SET_NULL, null=True, blank=True)
    supporting_detail = models.TextField(blank=True, null=True)
    description = models.TextField()
    is_recommended = models.BooleanField(default=False)
    def __str__(self):
        return self.name

    @property
    def is_generic(self):
        return self.subject is None
