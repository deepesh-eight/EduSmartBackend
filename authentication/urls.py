from django.urls import path

from .admin_views import *
from .views import *
from django.contrib.auth import views as auth_views
from .views import CustomPasswordResetAPIView

urlpatterns = [
    path('users/create/', UserCreateView.as_view(), name='user_create'),
    path('users/login/', LoginView.as_view(), name='user_login'),
    path('fetch/user/detail/<int:pk>/', FetchUserDetailView.as_view(), name='fetch_user_detail'),
    path('users/list/', UsersList.as_view(), name='users_list'),
    path('user/delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
    path('user/update-profile/', UserUpdateProfileView.as_view(), name='update_profile'),
    path('update-fcm-token/', FCMTokenUpdateView.as_view(), name='update_fcm_token'),

    # Admin Panel APIS
    path('staff/login/', AdminStaffLoginView.as_view(), name='staff_login'),
    path('staff/create/', AdminStaffCreateView.as_view(), name='staff_create'),
    path('staff/get-profile/', StaffProfileView.as_view(), name='staff_profile'),
    path('staff/get-profile/<int:pk>/', GetStaffView.as_view(), name='get_staff'),
    path('staff/update-profile/<int:pk>/', StaffUpdateProfileView.as_view(), name='staff_update_profile'),
    path('staff/delete/<int:pk>/', AdminStaffDeleteView.as_view(), name='staff_delete'),
    path('user/list/', UserListView.as_view(), name='user_list'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),

    # Non teaching staff APIS
    path('non-teaching-staff/create/', NonTeachingStaffCreateView.as_view(), name='staff_create'),
    path('non-teaching-staff/fetch/list/', NonTeachingStaffListView.as_view(), name='staff_list'),
    path('non-teaching-staff/fetch/detail/<int:pk>/', NonTeachingStaffDetailView.as_view(), name='staff_detail'),
    path('non-teaching-staff/delete/<int:pk>/', NonTeachingStaffDeleteView.as_view(), name='staff_delete'),
    path('non-teaching-staff/update/<int:pk>/', NonTeachingStaffUpdateView.as_view(), name='staff_update'),
    path('non-teaching-staff/profile-update/<int:pk>/', StaffUpdateView.as_view(), name='staff_profile_update'),

    # Non-teaching staff attendence API's
    path('attendance/create/', AttendanceCreateView.as_view(), name='attendance_create'),
    path('attendance/detail/<int:pk>/', FetchAttendanceDetailView.as_view(), name='fetch_attendance_detail'),
    path('attendance/list/', FetchAttendanceListView.as_view(), name='fetch_attendance_list'),
    path('attendance/filter/list/', StaffAttedanceFilterListView.as_view(), name='staff_attendance_filter_list'),

    # Notification
    path('notification/create/', NotificationCreateView.as_view(), name='notification_create'),
    path('notification/get/', NotificationListView.as_view(), name='notification_get'),
    path('notification/clear/', NotificationDeleteView.as_view(), name='notification_delete'),

    # Announcement
    path('announcement/create/', AnnouncementCreateView.as_view(), name='announcement_create'),
    path('announcement/list/', AnnouncementListView.as_view(), name='announcement_create'),

    # Mobile App user profile
    path('users/logout/', LogoutView.as_view(), name='user_logout'),
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),

    # Mobile App teacher schedule
    path('teacher/schedule/', TeacherUserScheduleView.as_view(), name='teacher_user_schedule'),

    # Mobile App teacher curriculum list
    path('curriculum/list/', TeacherCurriculumListView.as_view(), name='teacher_curriculum_list'),
    path('curriculum/class/list/', TeacherCurriculumCListView.as_view(), name='teacher_class_list'),
    path('curriculum/section/list/', TeacherCurriculumSectionListView.as_view(), name='teacher_section_list'),
    path('curriculum/subject/list/', TeacherCurriculumSubjectListView.as_view(), name='teacher_subject_list'),

    # Mobile App teacher day & review
    path('teacher/day/review/', TeacherDayReviewView.as_view(), name='teacher_day_review'),
    path('teacher/day/review/detail/<int:pk>/', TeacherDayReviewDetailView.as_view(), name='teacher_day_review_detail'),
    path('teacher/day/review/list/', TeacherDayReviewListView.as_view(), name='teacher_day_review_list'),

    # Mobile App teacher attendance
    path('teacher/attendance/', FetchTeacherAttendanceView.as_view(), name='fetch_teacher_attendance'),

    # Mobile App student timetable created by teacher
    path('create/timetable/', CreateTimetableView.as_view(), name='create_timetable'),
    path('undeclared/timetable/list/', UndeclaredTimetableView.as_view(), name='undeclared_timetable_list'),
    path('declared/timetable/list/', DeclaredTimetableView.as_view(), name='declared_timetable_list'),
    path('timetable/detail/<int:pk>/', TimetableDetailView.as_view(), name='timetable_detail'),
    path('timetable/delete/<int:pk>/', TimetableDeleteView.as_view(), name='timetable_delete'),
    path('timetable/update/<int:pk>/', TimetableUpdateView.as_view(), name='timetable_update'),
    path('declare/timetable/', DeclareTimetableView.as_view(), name='declare_timetable'),

    # Mobile App student exam report card created by teacher
    path('create/exam/report/', CreateExamReportView.as_view(), name='create_exam_report'),
    path('declare/exam/report/', DeclareExamReportView.as_view(), name='declare_exam_report'),
    path('declared/exam/report/list/', DeclaredExamReportListView.as_view(), name='declared_exam_report_list'),
    path('undeclared/exam/report/list/', UndeclaredExamReportListView.as_view(), name='undeclared_exam_report_list'),
    path('exam/report/card/delete/<int:pk>/', ExamReportCardDeleteView.as_view(), name='exam_report_delete'),
    path('exam/report/card/detail/<int:pk>/', ExamReportCardDetailView.as_view(), name='exam_report_detail'),
    path('exam/report/card/update/<int:pk>/', ExamReportCardUpdateView.as_view(), name='exam_report_update'),
    path('student/list/', StudentList.as_view(), name='student_list'),
    path('student/subject/list/', StudentSubjectListView.as_view(), name='student_subject-list'),

    # Mobile App zoom link
    path('create/zoomlink/', CreateZoomLinkView.as_view(), name='create_zoom_link'),
    path('zoomlink/list/', ZoomLinkListView.as_view(), name='zoom_link_list'),

    # Mobile Study material
    path('study/material/upload/', UploadStudyMaterialView.as_view(), name='upload_study_material'),
    path('study/material/list/', StudyMaterialListView.as_view(), name='study_material_list'),
    path('study/material/detail/<int:pk>/', StudyMaterialDetailView.as_view(), name='study_material_detail'),
    path('study/material/update/<int:pk>/', StudyMaterialUpdateView.as_view(), name='study_material_update'),
    path('study/material/delete/<int:pk>/', StudyMaterialDeleteView.as_view(), name='study_material_delete'),

    # Mobile E-book
    path('book/content/list/', AdminBookContentList.as_view(), name='book_content_list'),
    path('book/content/detail/<int:pk>/', AdminBookContentDetailView.as_view(), name='content-detail'),
    path('book/create/', RecommendedBookCreateView.as_view(), name='create_recommended_book'),

    # Mobile Class Event Image
    path('class/event/create/', ClassEventCreate.as_view(), name='class_event_create'),
    path('class/event/list/', ClassEventListView.as_view(), name='class_event_list'),
    path('class/event/detail/<int:pk>/', ClassEventDetailView.as_view(), name='class_event_detail'),
    path('class/event/update/<int:pk>/', ClassEventUpdateView.as_view(), name='class_event_update'),
    path('class/event/delete/<int:pk>/', ClassEventDeleteView.as_view(), name='class_event_delete'),

    # Events
    path('events/create', EventCreateView.as_view(), name='create_event'),
    path('events/get-events', GetAllEvents.as_view(), name='get_events'),
    path('calendar/list/', CalendarListView.as_view(), name='calendar_list'),
    path('event/list/', EventListView.as_view(), name='event_list'),
    path('event/detail/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('event/delete/<int:pk>/', EventDeleteView.as_view(), name='event_delete'),
    path('event/dashboard/list/', EventDashboardListView.as_view(), name='dashboard_event_list'),
    # TimeTable API for dashboard
    path('exam/schedule/list/', ExamScheduleListView.as_view(), name='exam_schedule_list'),
    path('exam/schedule/detail/', ExamScheduleDetailView.as_view(), name='exam_schedule_detail'),

    # Mobile Event API
    path('teacher/event/list/', TeacherEventListView.as_view(), name='teacher_event_list'),
    path('teacher/event/detail/<int:pk>/', TeacherEventDetailView.as_view(), name='teacher_event_detail'),
    path('teacher/calendar/list/', TeacherCalendarListView.as_view(), name='teacher_calendar_list'),
    path('teacher/calendar/detail/<int:pk>/', TeacherCalendarDetailView.as_view(), name='teacher_calendar_detail'),

    # Mobile Teacher 'student information'
    path('student/info/list/', StudentInfoListView.as_view(), name='student_info_list'),
    path('student/info/detail/<int:pk>/', StudentInfoDetailView.as_view(), name='student_info_detail'),

    # Mobile send notification
    path('student/remark/', StudentRemorkView.as_view(), name='student_remark'),

    # Inquiry Related API'S
    path('inquiry/', InquiryCreateView.as_view(), name='inquiry_create'),
    path('inquiries/', InquiryListView.as_view(), name='inquiry_list'),
    path('inquiry/<int:pk>/', InquiryDetailView.as_view(), name='inquiry_detail'),

    # Password reset views
    path('password_reset/', CustomPasswordResetAPIView.as_view(), name='password_reset_api'),

    # Password reset confirmation views (built-in Django views)
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
