from django.urls import path
from .views import *

urlpatterns = [
        path('teacher/users/create/', TeacherUserCreateView.as_view(), name='teacher_user_create'),
        path('fetch/teacher/detail/<int:pk>/', FetchTeacherDetailView.as_view(), name='fetch_student_detail'),
        path('teacher/list/', TeacherListView.as_view(), name='student_list'),
        path('teacher/delete/<int:pk>/', TeacherDeleteView.as_view(), name='teacher_delete'),
        path('teacher/update-profile/<int:pk>/', TeacherUpdateProfileView.as_view(), name='update_teacher_profile'),
        path('teacher/user/login/', TeacherLoginView.as_view(), name='teacher_login'),

        #Teacher schedule API'S
        path('schedule/create/', TeacherScheduleCreateView.as_view(), name='schedule_create'),
        path('schedule/detail/<int:pk>/', TeacherScheduleDetailView.as_view(), name='schedule_detail'),
        path('schedule/list/', TeacherScheduleListView.as_view(), name='schedule_list'),
        path('schedule/delete/<int:pk>/', TeacherScheduleDeleteView.as_view(), name='schedule_delete'),
        path('schedule/update/<int:pk>/', TeacherScheduleUpdateView.as_view(), name='schedule_update'),
]