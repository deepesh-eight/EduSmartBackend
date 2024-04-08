from django.contrib import admin

from authentication.models import ErrorLogging, User, SuperAdminUser, AdminUser, ManagementUser, TeacherUser, \
    StudentUser, Certificate


# Register your models here.

@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ('email', 'username')
@admin.register(ErrorLogging)
class ErrorLoggingAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'context', 'exception', 'traceback')
    list_filter = ('created_at',)
    search_fields = ('context', 'exception', 'traceback')

@admin.register(TeacherUser)
class TeacherUser(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'dob', 'image', 'gender', 'joining_date', 'religion', 'blood_group', 'ctc', 'address', 'role', 'experience',
                    'class_subject_section_details', 'highest_qualification')

@admin.register(StudentUser)
class StudentUser(admin.ModelAdmin):
    list_display = ('user', 'name', 'dob', 'image', 'father_name', 'father_phone_number', 'mother_name', 'mother_occupation', 'mother_phone_number', 'gender',
                    'father_occupation', 'admission_date', 'school_fee', 'bus_fee', 'canteen_fee', 'other_fee', 'due_fee', 'total_fee', 'religion',
                    'blood_group', 'class_enrolled', 'section', 'curriculum', 'permanent_address', 'bus_number', 'bus_route')

@admin.register(Certificate)
class Certificate(admin.ModelAdmin):
    list_display = ('user', 'certificate_file')