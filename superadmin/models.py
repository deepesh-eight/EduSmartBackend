from django.contrib.auth.hashers import make_password
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class SchoolProfile(models.Model):
    logo = models.ImageField(upload_to='', blank=True)
    school_name = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=200,null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    established_year = models.IntegerField(null=True, blank=True)
    school_type = models.CharField(max_length=255, null=True, blank=True)
    principle_name = models.CharField(max_length=255, null=True, blank=True)
    contact_no = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(unique=True)
    school_website = models.CharField(max_length=255, null=True, blank=True)
    school_id = models.CharField(max_length=200, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def get_contact_no_without_country_code(self):
        if not self.contact_no:
            return None
        return str(self.contact_no.as_national.lstrip('0').strip().replace(' ', ''))

    def set_password(self, raw_password):
        self.password = make_password(raw_password)


class SchoolProfilePassword(models.Model):
    school = models.ForeignKey(SchoolProfile, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)


class Announcement(models.Model):
    creator_name = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    announcement_title = models.CharField(max_length=255)
    description = models.TextField()
