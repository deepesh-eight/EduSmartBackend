from django.contrib.auth.hashers import make_password
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from authentication.models import User


# Create your models here.


class SchoolProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    logo = models.ImageField(upload_to='', blank=True)
    school_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=200,null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    school_type = models.CharField(max_length=255, null=True, blank=True)
    principle_name = models.CharField(max_length=255, null=True, blank=True)
    contact_no = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    school_website = models.CharField(max_length=255, null=True, blank=True)
    school_id = models.CharField(max_length=200, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class SchoolProfilePassword(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)


class Announcement(models.Model):
    creator_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255, default="super admin")
    date_time = models.DateTimeField(auto_now=True)
    announcement_title = models.CharField(max_length=255)
    description = models.TextField()
