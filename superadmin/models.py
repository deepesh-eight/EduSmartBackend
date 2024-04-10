from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
# Create your models here.


class SchoolProfile(models.Model):
    logo = models.ImageField(upload_to='', blank=True)
    school_name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=200)
    state = models.CharField(max_length=200)
    established_year = models.IntegerField()
    school_type = models.CharField(max_length=255)
    principle_name = models.CharField(max_length=255)
    contact_no = PhoneNumberField(blank=True, null=True)
    email = models.EmailField(unique=True)
    school_website = models.CharField(max_length=255)
    description = models.TextField()

    def get_contact_no_without_country_code(self):
        if not self.contact_no:
            return None
        return str(self.contact_no.as_national.lstrip('0').strip().replace(' ', ''))


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
