from django.urls import path
from .views import *

urlpatterns = [
        path('profile/', ManagementProfileView.as_view(), name='management_profile'),

        # Exam timetable
        path('current/exam/timetable/', CurrentExamTimeTableView.as_view(), name='current_exam_timetable'),
        ]