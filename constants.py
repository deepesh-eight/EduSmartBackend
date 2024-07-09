USER_TYPE_CHOICES = [
    ('admin', 'Admin'),
    ('management', 'Management'),
    ('student', 'Student'),
    ('teacher', 'Teacher'),
    ('payrollmanagement', 'PayrollManagement'),
    ('boarding', 'Boarding'),
    ('non-teaching', 'Non-teaching')
]

GENDER_CHOICES = [
    ('male', 'Male'),
    ('female', 'female'),
    ('other', 'Other'),
]

RELIGION_CHOICES = [
    ('christian', 'Christian'),
    ('islam', 'Islam'),
    ('hinduism', 'Hinduism'),
    ('buddhism', 'Buddhism'),
    ('sikhism', 'Sikhism'),
    ('judaism', 'Judaism'),
    ('other', 'Other'),
]
BLOOD_GROUP_CHOICES = [
    ('A+', 'A+'),
    ('A-', 'A-'),
    ('B+', 'B+'),
    ('B-', 'B-'),
    ('AB+', 'AB+'),
    ('AB-', 'AB-'),
    ('O+', 'O+'),
    ('O-', 'O-'),
]

CLASS_CHOICES = [
    ('1st', '1st'),
    ('2nd', '2nd'),
    ('3rd', '3rd'),
    ('4th', '4th'),
    ('5th', '5th'),
    ('6th', '6th'),
    ('7th', '7th'),
    ('8th', '8th'),
    ('9th', '9th'),
    ('10th', '10th'),
    ('11th', '11th'),
    ('12th', '12th'),
]

SUBJECT_CHOICES = [
    ("english", "english"),
    ("hindi", "hindi"),
    ("maths", "maths"),
    ("science", "science"),
]
ROLE_CHOICES = [
    ("teacher", "teacher"),
    ("class teacher", "class teacher")
]

ATTENDENCE_CHOICE = [
    ("P", "present"),
    ("A", "Absent"),
    ("L", "On_leave")
]

EXAME_TYPE_CHOICE = [
    ('Annual Exams', 'Annual Exams'),
    ('Half Yearly Exams', 'Half Yearly Exams'),
    ('Quarterly Exams', 'Quarterly Exams'),
    ('Pre-Board Exams', 'Pre-Board Exams'),
    ('Monthly Test', 'Monthly Test')
]

CONTENT_TYPES = [
    ('e_book', 'E-Book'),
    ('e_video', 'E-Video'),
]

CATEGORY_TYPES = [
    ('class content', 'class content'),
    ('other', 'other'),
]

month_mapping = {
    'January': 1,
    'February': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9,
    'October': 10,
    'November': 11,
    'December': 12,
}

class UserLoginMessage:
    USER_DOES_NOT_EXISTS = "User does not exists."
    INCORRECT_PASSWORD = "Incorrect password, please try again."
    SIGNUP_SUCCESSFUL = "User Signup successful."
    STAFF_ALREADY_EXISTS = "Staff email or phone already exists"
    USER_LOGIN_SUCCESSFUL = "User login successfully."


class UserResponseMessage:
    USER_DOES_NOT_EXISTS = "User does not exists."
    USER_NOT_FOUND = "User not found"
    USER_DETAIL_MESSAGE = "User detail fetch successfully."
    USER_LIST_MESSAGE = "All user's fetch successfully."
    USER_DELETE_MESSAGE = "User deleted successfully."
    PROFILE_UPDATED_SUCCESSFULLY = "User profile updated successfully"
    EMAIL_ALREADY_EXIST = "Email already exist."
    TOKEN_HAS_EXPIRED = "Token has expired."


class CurriculumMessage:
    CURRICULUM_CREATED_SUCCESSFULLY = "Curriculum created successfully."
    CURRICULUM_LIST_MESSAGE = "All curriculum fetch successfully."
    CURRICULUM_DELETED_SUCCESSFULLY = "Curriculum deleted successfully."
    CURRICULUM_NOT_FOUND = "Curriculum not found."
    CURRICULUM_DETAIL_MESSAGE = "Curriculum detail fetch successfully."
    CURRICULUM_UPDATED_MESSAGE = "Curriculum updated successfully."
    CLASSES_LIST_MESSAGE = "All classes fetch successfully."
    SUBJECT_LIST_MESSAGE = "All subject fetch successfully."
    SECTION_LIST_MESSAGE = "Section list fetch successfully."
    TEACHER_LIST_MESSAGE = "Teacher list fetch successfully."


class ScheduleMessage:
    SCHEDULE_CREATED_SUCCESSFULLY = "Schedule created successfully.",
    SCHEDULE_FETCHED_SUCCESSFULLY = "Schedule fetched successfully."
    SCHEDULE_NOT_FOUND = "Schedule not found."
    SCHEDULE_DELETED_SUCCESSFULLY = "Schedule deleted successfully.",
    SCHEDULE_LIST_MESSAGE = "All schedule fetch successfully."
    SCHEDULE_UPDATED_SUCCESSFULLY = "Teacher schedule updated successfully"
    SCHEDULE_renew_SUCCESSFULLY = "Teacher schedule renew successfully"


class AttendenceMarkedMessage:
    ATTENDENCE_MARKED_SUCCESSFULLY = "Attendance marked successfully."
    ATTENDANCE_FETCHED_SUCCESSFULLY = 'Attendance fetched successfully.'
    STUDENT_ATTENDANCE_FETCHED_SUCCESSFULLY = 'Student attendance fetched successfully.'


class SchoolMessage:
    SCHOOL_CREATED_SUCCESSFULLY = "School created successfully."
    SCHOOL_DETAIL_MESSAGE = "School profile fetch successfully."
    SCHOOL_DOES_NOT_EXISTS = "School does not exists."
    SCHOOL_PROFILE_UPDATED_SUCCESSFULLY = "School profile updated successfully"
    SCHOOL_EMAIL_ALREADY_EXIST = "School with this email already exist."
    SCHOOL_DELETED_SCCCESSFULLY = "School profile deleted successfully."


class DayReviewMessage:
    DAY_REVIEW_CREATED_SUCCESSFULLY = "Day and review created successfully."
    DAY_REVIEW_FETCHED_SUCCESSFULLY = "Day and review detail fetch successfully."
    DAY_REVIEW_NOT_FOUND = "Day and review not found."
    DAY_REVIEW_LIST_FETCHED_SUCCESSFULLY = "Day and review list fetch successfully."


class NotificationMessage:
    NOTIFICATION_CREATED_SUCCESSFULLY = "Notification created successfully."
    NOTIFICATION_FETCHED_SUCCESSFULLY = "Notification fetched successfully."
    STUDENT_REMARK_NOTIFICATION = "send a remark."


class AnnouncementMessage:
    ANNOUNCEMENT_CREATED_SUCCESSFULLE = "Announcement created successfully."
    ANNOUNCEMENT_FETCHED_SUCCESSFULLE = "Announcement fetched successfully."


class TimeTableMessage:
    TIMETABLE_CREATED_SUCCESSFULLY = "Timetable created successfully."
    UNDECLARED_TIMETABLE_FETCHED_SUCCESSFULLY = "Undeclared timetable fetched successfully."
    DECLARED_TIMETABLE_FETCHED_SUCCESSFULLY = "declared timetable fetched successfully."
    TIMETABLE_FETCHED_SUCCESSFULLY = "Timetable fetched successfully."
    TIMETABLE_NOT_EXIST = "Timetable does not exist."
    TIMETABLE_DELETED_SUCCESSFULLY = "Timetable deleted successfully."
    TIMETABLE_UPDATED_SUCCESSFULLY = "Timetable updated successfully."
    TIMETABLE_DECLARE_SUCCESSFULLY = "Timetable declare successfully."


class ReportCardMesssage:
    REPORT_CARD_CREATED_SUCCESSFULLY = "Report card created successfully."
    REPORT_CARD_FETCHED_SUCCESSFULLY = "Report card fetched successfully."
    REPORT_CARD_DELETED_SUCCESSFULLY = "Report card deleted successfully."
    REPORT_CARD_UPDATED_SUCCESSFULLY = "Report card updated successfully."
    REPORT_CARD_list_SUCCESSFULLY = "All report card fetched successfully."
    REPORT_CARD_DECLARE_SUCCESSFULLY = "Report card declare successfully."
    UNDECLARED_REPORT_CARD_FETCHED_SUCCESSFULLY = "Undeclared report card fetched successfully."
    DECLARED_REPORT_CARD_FETCHED_SUCCESSFULLY = "declared report card fetched successfully."
    REPORT_CARD_NOT_EXIST = "Report card does not exist."


class ZoomLinkMessage:
    ZOOM_LINK_UPLOADED_SUCCESSFULLY = "Zoom link uploaded successfully."
    ZOOM_LINK_FETCHED_SUCCESSFULLY = "Zoom link fetched successfully."


class StudyMaterialMessage:
    STUDY_MATERIAL_UPLOADED_SUCCESSFULLY = "Study material uploaded successfully."
    STUDY_MATERIAL_FETCHED_SUCCESSFULLY = "Study material fetched successfully."
    STUDY_MATERIAL_Not_Exist = "Study material does not exist."
    STUDY_MATERIAL_DELETED_SUCCESSFULLY = "Study material deleted successfully."
    STUDY_MATERIAL_UPDATED_SUCCESSFULLY = "Study material updated successfully."

class EventsMessages:
    EVENT_CREATED_SUCCESSFULLY = "Event Created Successfully."
    EVENT_PROVIDE_ALL_INFORMATION = "Please provide all information"
    PROVIDE_VALID_DATE = "Please Provide Valid Date"
    EVENTS_DATA_FETCHED_SUCCESSFULLY = "Events Data Fetched Successfully."
    EVENT_DATA_NOT_EXIST = "Event does not exist."
    EVENT_DATA_DELETED = "Event deleted successfully."

class BusMessages:
    BUS_ROUTE_CREATED = "Route Created Successfully."
    ROUTE_DATA_FETCHED = "Route Data Fetched Successfully."
    BUS_ADDED = "Bus Added Successfully."
    BUS_DATA_FETCHED = "Bus Data Fetched Successfully."
    BUS_DELETED = "Bus Deleted Successfully."
    BUS_NOT_FOUND = "Bus Not Found."
    BUS_UPDATED = "Bus detail updated successfully."
    BUS_ROUTE_NOT_FOUND = "Bus route Not Found."
    BUS_ROUTE_DELETED = "Bus route deleted Successfully."
    BUS_ROUTE_UPDATED = "Bus route updated successfully."


class ContentMessages:
    CONTENT_CREATED = "Content Created Successfully."
    CONTENT_FETCHED = "Content Fetched Successfully."
    CONTENT_DELETED = "Content Deleted Successfully."
    CONTENT_UPDATED = 'Content updated Successfully.'
    CONTENT_NOT_EXIST = 'Content does not exist.'


class ClassEventMessage:
    CLASS_EVENT_CREATED = "Class Event created successfully."
    CLASS_EVENT_LIST = "Class event fetched successfully."
    CLASS_EVENT_NOT_EXIST = "Class event does not exist."
    CLASS_EVENT_UPDATED = "Class event updated successfully."
    CLASS_EVENT_DELETED = "Class event deleted successfully."


class TeacherAvailabilityMessage:
    TEACHER_AVAILABILITY_CREATED = "Teacher availability created successfully."
    TEACHER_AVAILABILITY_UPDATED = "Teacher availability updated successfully."
    TEACHER_AVAILABILITY_NOT_EXIST = "Teacher availability is not  available."
    TEACHER_AVAILABILITY_TIME = "Teacher availability time fetch successfully."
    TEACHER_AVAILABILITY_ALREADY_CREATED = "Teacher availability already created for this teacher."


class ChatMessage:
    CHAT_REQUEST_CREATED = "Chat request created successfully with the teacher."
    CHAT_HISTORY_FETCH = "Chat history fetched successfully."
    CHAT_REQUEST_GET = "Chat request get successfully."
    CHAT_REQUEST_ALREADY_CREATED = "Chat request already created for this time."
    CHAT_REQUEST_ACCEPTED = "Chat request accepted successfully."
    CHAT_JOIN = "Chat join successfully."
    CHAT_REQUEST_CANCEL = "Chat cancel successfully."


class InquiryMessage:
    INQUIRY_SUBMITTED_SUCCESSFULLY = "Inquiry submitted successfully."
    INQUIRY_LIST_FETCH_SUCCESSFULLY = "Inquiry list fetched successfully."
    INQUIRY_DETAIL_FETCH_SUCCESSFULLY = "Inquiry detail fetched successfully."
    INQUIRY_DATA_FETCH_SUCCESSFULLY = "Inquiry data not exist."


class SalaryMessage:
    SALARY_ADDED_SUCCESSFULLY = "Salary added successfully."
    SALARY_DETAIL_FETCH_SUCCESSFULLY = "Salary detail fetched successfully."
    SALARY_DETAIL_NOT_EXIST = "Salary detail does not exist."
    SALARY_UPDATED_SUCCESSFULLY = "Salary detail updated successfully."


class FeeMessage:
    FEE_ADDED_SUCCESSFULLY = "Fee added successfully."
    FEE_DETAIL_FETCH_SUCCESSFULLY = "Fee detail fetched successfully."
    FEE_DETAIL_NOT_EXIST = "Fee detail does not exist."
    FEE_UPDATED_SUCCESSFULLY = "Fee detail updated successfully."