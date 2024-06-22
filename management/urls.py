from django.urls import path
from .views import *

urlpatterns = [
        path('profile/', ManagementProfileView.as_view(), name='management_profile'),

        # Exam timetable
        path('exam/timetable/', ExamTimeTableView.as_view(), name='exam_timetable'),
        path('exam/timetable/detail/<int:pk>/', ExamTimeTableDetailView.as_view(), name='exam_timetable_detail'),
        path('exam/timetable/delete/<int:pk>/', ExamTimeTableDeleteView.as_view(), name='exam_timetable_delete'),

        # Exam report card
        path('exam/report/card/', ExamReportCardListView.as_view(), name='exam_report_card_list'),
        path('exam/report/card/filter/', ExamReportCardFilterListView.as_view(), name='exam_report_card_filter_list'),
        ]