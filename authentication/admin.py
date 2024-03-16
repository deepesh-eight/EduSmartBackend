from django.contrib import admin

from authentication.models import ErrorLogging, User, SuperAdminUser, AdminUser, ManagementUser, TeacherUser


# Register your models here.

@admin.register(User)
class User(admin.ModelAdmin):
    list_display = ('email', 'username')
@admin.register(ErrorLogging)
class ErrorLoggingAdmin(admin.ModelAdmin):
    list_display = ('created_at', 'context', 'exception', 'traceback')
    list_filter = ('created_at',)
    search_fields = ('context', 'exception', 'traceback')