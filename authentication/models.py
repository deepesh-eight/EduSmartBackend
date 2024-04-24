import datetime
import json

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_admin_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("user_type", "admin")
        return self._create_user(email, password, **extra_fields)

    def create_user(self, email, password=None, user_type="default", **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        if user_type == "management":
            extra_fields.setdefault("user_type", "management")
        elif user_type == "payrollmanagement":
            extra_fields.setdefault("user_type", "payrollmanagement")
        elif user_type == "boarding":
            extra_fields.setdefault("user_type", "boarding")
        elif user_type == 'teacher':
            extra_fields.setdefault("user_type", "teacher")
        elif user_type == 'student':
            extra_fields.setdefault("user_type", "student")
        elif user_type == 'non-teaching':
            extra_fields.setdefault("user_type", "non-teaching")
        return self._create_user(email, password, **extra_fields)


    def create_superuser(self, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_type", "SuperAdmin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('management', 'Management'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('payrollmanagement', 'PayrollManagement'),
        ('boarding', 'Boarding'),
        ('non-teaching', 'Non-teaching')
    ]

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    old_id = models.IntegerField(null=True, blank=True)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    username = None
    first_name = None
    last_name = None
    phone = PhoneNumberField(blank=True, null=True)
    designation = models.CharField(max_length=150, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    school_id = models.CharField(max_length=255, null=True, blank=True)

    EMAIL_FIELD = "email"
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    objects = UserManager()

    def get_full_name(self):
        full_name = "%s" % (self.name)
        return full_name.strip()

    def get_short_name(self):
        return self.name

    def get_phone_without_country_code(self):
        if not self.phone:
            return None
        return str(self.phone.as_national.lstrip('0').strip().replace(' ', ''))

    def get_address_string(self):
        address_details = self.address_details.filter(is_default=True).first()
        if not address_details:
            return None
        address = f'{address_details.address_line_1}, {address_details.city}, {address_details.state}, {address_details.country} - {address_details.pincode}'
        return address

class SuperAdminUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class AdminUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class ManagementUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Class(models.Model):
    class_name = models.CharField(max_length=50)
    section = models.CharField(max_length=100)

    def __str__(self) -> str:
        return f'{self.name} - {self.section}'

class TeacherUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    image = models.ImageField(upload_to='', blank=True)
    gender = models.CharField(max_length=50)
    joining_date = models.DateField(auto_now_add=True, null=True, blank=True)
    religion = models.CharField(max_length=50)
    blood_group = models.CharField(max_length=50)
    ctc = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    # class_taught = models.ManyToManyField(Class)
    address = models.TextField(blank=True,null=True)
    role = models.CharField(max_length=255)
    experience = models.IntegerField(null=True,blank=True)
    class_subject_section_details = models.JSONField(blank=True, null=True)
    highest_qualification = models.CharField(max_length=255)
    # certificate = models.FileField(upload_to='', blank=True, null=True)

    def __str__(self) -> str:
        return f'{self.id}'


class StaffUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(255)
    last_name = models.CharField(255)
    image = models.ImageField(upload_to='', blank=True)
    gender = models.CharField(max_length=50)
    dob = models.DateField(default=datetime.date.today)
    blood_group = models.CharField(max_length=50, blank=True, null=True)
    religion = models.CharField(max_length=100)
    role = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    joining_date = models.DateField(auto_now_add=True, null=True, blank=True)
    ctc = models.DecimalField(max_digits=16, decimal_places=2, default=0.0)

    def __str__(self) -> str:
        return f'{self.id}'


class Certificate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='certificates')
    certificate_file = models.FileField(upload_to='')


class StudentUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    dob = models.DateField(default=datetime.date.today)
    image = models.ImageField(upload_to='', blank=True)
    father_name = models.CharField(max_length=150, null=True, blank=True)
    father_phone_number = PhoneNumberField(blank=True, null=True)
    mother_name = models.CharField(max_length=150,null=True, blank=True)
    mother_occupation = models.CharField(max_length=255,null=True, blank=True)
    mother_phone_number = PhoneNumberField(blank=True, null=True)
    gender = models.CharField(max_length=50)
    father_occupation = models.CharField(max_length=255)
    admission_date = models.DateField(default=datetime.date.today)
    school_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    bus_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    canteen_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    other_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    due_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    religion = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=50, blank=True, null=True)
    class_enrolled = models.CharField(max_length=255)
    section = models.CharField(max_length=50)
    curriculum = models.ForeignKey('curriculum.Curriculum', on_delete=models.CASCADE, null=True, blank=True)
    permanent_address = models.TextField(blank=True, null=True)
    bus_number = models.CharField(max_length=255)
    bus_route = models.IntegerField()

    def __str__(self) -> str:
        return f'{self.id}'

    def get_phone_without_country_code(self):
        if not self.phone:
            return None
        return str(self.phone.as_national.lstrip('0').strip().replace(' ', ''))

    def set_subject(self, subject):
        self.subject = json.dumps(subject)

    def get_subject(self):
        return json.loads(self.subject)

class PayrollManagementUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class AddressDetails(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='address_details')
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=255)
    pincode = models.CharField(max_length=10)
    is_default = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.user} address details'

class ErrorLogging(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    context = models.TextField(blank=True, null=True)
    exception = models.TextField(blank=True, null=True)
    traceback = models.TextField(blank=True, null=True)

class TeachersSchedule(models.Model):
    start_date = models.DateField(default=datetime.date.today)
    end_date = models.DateField(default=datetime.date.today)
    teacher = models.ForeignKey(TeacherUser, on_delete=models.CASCADE, blank=True, null=True)
    schedule_data = models.JSONField(null=True)

class TeacherAttendence(models.Model):
    teacher = models.ForeignKey(TeacherUser, on_delete=models.CASCADE)
    date = models.DateField()
    mark_attendence = models.CharField(max_length=100)

class StaffAttendence(models.Model):
    staff = models.ForeignKey(StaffUser, on_delete=models.CASCADE)
    date = models.DateField()
    mark_attendence = models.CharField(max_length=100)


class EventsCalender(models.Model):
    day_event = models.CharField(max_length=200) # This will be choice field it can be one_day_event or multi_day_event.
    event_date = models.DateField()
    calendar = models.CharField(max_length=200) # This will be choice field it can be academic_calendar or events.
    title = models.CharField(max_length=255)
    description = models.TextField()
    event_image = models.ImageField(upload_to='', blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class DayReview(models.Model):
    school_id = models.CharField(max_length=255, null=True, blank=True)
    class_name = models.CharField(max_length=100)
    section = models.CharField(max_length=150)
    subject = models.CharField(max_length=255)
    discription = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Notification(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField()
    date_time = models.DateTimeField(auto_now=True)  # Automatically set to the current time on every save
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.CharField(max_length=100, default=0)
    reciver_id = models.CharField(max_length=100, null=True)
    class_id = models.CharField(max_length=255, null=True)

    def __str__(self):
        return self.title