from django.urls import path
from .views import *

urlpatterns = [
        path('profile/', ManagementProfileView.as_view(), name='management_profile'),

        # Exam timetable
        path('exam/timetable/', ExamTimeTableView.as_view(), name='exam_timetable'),
        ]