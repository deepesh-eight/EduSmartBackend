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
        path('get_student_attendance/', StudentAttendanceView.as_view(), name='get_specific_student_attandance'),

        #Student API's for Mobile
        path('mobile/student/list/', FetchStudentList.as_view(), name='fetch_student_list'),
        path('mobile/attendance/create/', StudentAttendanceCreateView.as_view(), name='attendance_create'),

        # Student curriculum API'S
        path('curriculum/list/', AdminCurriculumList.as_view(), name='admin_curriculum_list'),
        path('classes/list/', AdminClassesList.as_view(), name='admin_classes_list'),
        path('optional/subject/list/', AdminOptionalSubjectList.as_view(), name='admin_optional_subject_list'),

        # Student Mobile API
        path('timetable/list/', StudentTimeTableListView.as_view(), name='student_timetable_list'),
        path('report/card/list/', StudentReportCardListView.as_view(), name='student_report_card_list'),
        path('report/card/filter/list/', StudentReportCardFilterListView.as_view(), name='student_report_card_filter_list'),
        path('study/material/list/', StudentStudyMaterialListView.as_view(), name='student_study_material_list'),
        path('study/material/detail/<int:pk>/', StudentStudyMaterialDetailView.as_view(), name='student_study_material_detail'),
        path('zoom/link/list/', StudentZoomLinkListView.as_view(), name='student_zoom_link_list'),

        # Student Mobile Content API
        path('e/book/list/', StudentEBookListView.as_view(), name='e_book_list'),
        path('e/book/detail/<int:pk>/', StudentEBookDetailView.as_view(), name='e_book_detail'),

        # Student Mobile Event API
        path('class/event/list/', StudentClassEventListView.as_view(), name='class_event_list'),
        path('class/event/detail/<int:pk>/', StudentClassEventDetailView.as_view(), name='class_event_detail'),

        # Student Mobile teacher day & review
        path('day/review/list/', StudentDayReview.as_view(), name='day_review_list'),

]