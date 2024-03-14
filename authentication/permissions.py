from rest_framework import permissions

from authentication.models import User, SuperAdminUser


def is_superadmin_user(user):
    return user.is_authenticated and isinstance(user, User) and (isinstance(user, SuperAdminUser) or user.is_superuser)


def is_admin_user(user):
    return user.is_authenticated and isinstance(user, User) and user.is_superuser


def is_student_user(user):
    return user.is_authenticated and isinstance(user, User) and user.user_type == "student"


def is_teacher_user(user):
    return user.is_authenticated and isinstance(user, User) and user.user_type == "teacher"


def is_management_user(user):
    return user.is_authenticated and isinstance(user, User) and user.user_type == "management"

def is_payrollmanagement_user(user):
    return user.is_authenticated and isinstance(user, User) and user.user_type == "payrollmanagement"

def is_boarding_user(user):
    return user.is_authenticated and isinstance(user, User) and user.user_type == "boarding"
class IsSuperAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_superadmin_user(request.user)

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_admin_user(request.user)

class IsStudentUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_student_user(request.user)

class IsTeacherUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_teacher_user(request.user)

class IsManagementUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_management_user(request.user)

class IsPayRollManagementUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_payrollmanagement_user(request.user)

class IsBoardingUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_boarding_user(request.user)
