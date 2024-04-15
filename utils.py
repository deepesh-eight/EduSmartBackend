import datetime

from django.contrib.auth import get_user_model

from authentication.models import TeacherAttendence, StaffAttendence
from student.models import StudentAttendence


def create_response_data(status, message, data):
    return {
        "status": status,
        "message": message,
        "data": data
    }
def create_response_list_data(status, count,message, data):
    return {
        "status": status,
        "count": count,
        "message": message,
        "data": data
    }


def generate_random_password():
    User = get_user_model()
    return get_user_model().objects.make_random_password()


def get_teacher_total_attendance(obj):
    teacher = obj.first()
    year = datetime.date.today().year
    total_attendance = TeacherAttendence.objects.filter(
        teacher=teacher.teacher, date__year=year, mark_attendence='P').count()
    return total_attendance


def get_teacher_monthly_attendance(obj):
    teacher = obj.first()
    today = datetime.date.today()
    month = today.month
    year = today.year
    monthly_attendance = TeacherAttendence.objects.filter(
        teacher=teacher.teacher, date__year=year, date__month=month, mark_attendence='P').count()
    return monthly_attendance


def get_teacher_total_absent(obj):
    teacher = obj.first()
    year = datetime.date.today().year
    total_absent = TeacherAttendence.objects.filter(
        teacher=teacher.teacher, date__year=year, mark_attendence='A').count()
    return total_absent


def get_teacher_monthly_absent(obj):
    teacher = obj.first()
    today = datetime.date.today()
    month = today.month
    year = today.year
    monthly_absent = TeacherAttendence.objects.filter(
        teacher=teacher.teacher, date__year=year, date__month=month, mark_attendence='A').count()
    return monthly_absent


def get_student_total_attendance(obj):
    student = obj.first()
    year = datetime.date.today().year
    total_attendance = StudentAttendence.objects.filter(
        student=student.student, date__year=year, mark_attendence='P').count()
    return total_attendance


def get_student_total_absent(obj):
    student = obj.first()
    year = datetime.date.today().year
    total_absent = StudentAttendence.objects.filter(
        student=student.student, date__year=year, mark_attendence='A').count()
    return total_absent


def get_student_attendence_percentage(obj):
    total_attendence = get_student_total_attendance(obj)
    total_school_days = 365
    attendence_percentage = (total_attendence/total_school_days) * 100
    return round(attendence_percentage)


def get_staff_total_attendance(obj):
    staff = obj.first()
    year = datetime.date.today().year
    total_attendance = StaffAttendence.objects.filter(
        staff=staff.staff, date__year=year, mark_attendence='P').count()
    return total_attendance


def get_staff_monthly_attendance(obj):
    staff = obj.first()
    today = datetime.date.today()
    month = today.month
    year = today.year
    monthly_attendance = StaffAttendence.objects.filter(
        staff=staff.staff, date__year=year, date__month=month, mark_attendence='P').count()
    return monthly_attendance


def get_staff_total_absent(obj):
    staff = obj.first()
    year = datetime.date.today().year
    total_absent = StaffAttendence.objects.filter(
        staff=staff.staff, date__year=year, mark_attendence='A').count()
    return total_absent


def get_staff_monthly_absent(obj):
    staff = obj.first()
    today = datetime.date.today()
    month = today.month
    year = today.year
    monthly_absent = StaffAttendence.objects.filter(
        staff=staff.staff, date__year=year, date__month=month, mark_attendence='A').count()
    return monthly_absent
