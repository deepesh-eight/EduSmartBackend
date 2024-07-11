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
        path('exam/report/card/detail/', StudentReportCardView.as_view(), name='report_card_detail'),

        # Salary related API'S
        path('add/salary/', AddSalaryView.as_view(), name='add_salary'),
        path('salary/detail/<int:pk>/', SalaryDetailView.as_view(), name='salary_detail'),
        path('salary/update/<int:pk>/', SalaryUpdateView.as_view(), name='salary_update'),

        #Fee related API'S
        path('add/fee/', AddFeeView.as_view(), name='add_fee'),
        path('fee/list/', FeeListView.as_view(), name='fee_list'),
        path('fee/update/<int:pk>/', FeeUpdateView.as_view(), name='fee_update'),
        path('fee/detail/<int:pk>/', FeeDetailView.as_view(), name='fee_detail'),

        #Student related API'S
        path('student/list/', StudentList.as_view(), name='student_list'),
        path('students/filter/list/', StudentFilterList.as_view(), name='student_filter_list'),

        ]