from django.urls import path
from .views import *

urlpatterns = [
        path('student/users/create/', StudentUserCreateView.as_view(), name='student_user_create'),
        path('fetch/student/detail/<int:pk>/', FetchStudentDetailView.as_view(), name='fetch_student_detail'),
        path('student/list/', StudentListView.as_view(), name='student_list'),
        path('student/delete/<int:pk>/', StudentDeleteView.as_view(), name='student_delete'),
        path('student/update-profile/<int:pk>/', StudentUpdateProfileView.as_view(), name='update_student_profile'),

        #Student attendence API's
        path('class/student/list/', ClassStudentListView.as_view(), name='class_attendance_list'),
        path('attendance/detail/<int:pk>/', FetchAttendanceDetailView.as_view(), name='fetch_attendance_detail'),
        path('attendance/list/',  FetchAttendanceListView.as_view(), name='fetch_attendance_list'),
        path('attendance/filter/list/',  FetchAttendanceFilterListView.as_view(), name='fetch_attendance_filter_list'),

        #Student API's for Mobile
        path('mobile/student/list/', FetchStudentList.as_view(), name='fetch_student_list'),
        path('mobile/attendance/create/', StudentAttendanceCreateView.as_view(), name='attendance_create'),

        # Student curriculum API'S
        path('curriculum/list/', AdminCurriculumList.as_view(), name='admin_curriculum_list'),
        path('classes/list/', AdminClassesList.as_view(), name='admin_classes_list'),
        path('optional/subject/list/', AdminOptionalSubjectList.as_view(), name='admin_optional_subject_list'),

]