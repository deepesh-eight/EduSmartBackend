from django.urls import path
from .views import *

urlpatterns = [
        path('student/users/create/', StudentUserCreateView.as_view(), name='student_user_create'),
        path('fetch/student/detail/<int:pk>/', FetchStudentDetailView.as_view(), name='fetch_student_detail'),
        path('student/list/', StudentListView.as_view(), name='student_list'),
        path('student/delete/<int:pk>/', StudentDeleteView.as_view(), name='student_delete'),
        path('student/update-profile/<int:pk>/', StudentUpdateProfileView.as_view(), name='update_student_profile'),
]