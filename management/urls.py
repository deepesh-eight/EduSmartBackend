from django.urls import path
from .views import *

urlpatterns = [
        path('profile/', ManagementProfileView.as_view(), name='management_profile'),

        # Exam timetable
        path('exam/timetable/', ExamTimeTableView.as_view(), name='exam_timetable'),
        path('exam/timetable/detail/<int:pk>/', ExamTimeTableDetailView.as_view(), name='exam_timetable_detail'),
        ]