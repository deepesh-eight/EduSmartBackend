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
    ("class_teacher", "class_teacher")
]

ATTENDENCE_CHOICE = [
    ("P", "present"),
    ("A", "Absent"),
    ("L", "On_leave")
]

class UserLoginMessage:
    USER_DOES_NOT_EXISTS = "User does not exists."
    INCORRECT_PASSWORD = "Incorrect password, please try again."
    SIGNUP_SUCCESSFUL = "User Signup successful."
    STAFF_ALREADY_EXISTS = "Staff email or phone already exists"


class UserResponseMessage:
    USER_DOES_NOT_EXISTS = "User does not exists."
    USER_NOT_FOUND = "User not found"
    USER_DETAIL_MESSAGE = "User detail fetch successfully."
    USER_LIST_MESSAGE = "All user's fetch successfully."
    USER_DELETE_MESSAGE = "User deleted successfully."
    PROFILE_UPDATED_SUCCESSFULLY = "User profile updated successfully"
    EMAIL_ALREADY_EXIST = "Email already exist."


class CurriculumMessage:
    CURRICULUM_CREATED_SUCCESSFULLY = "Curriculum created successfully."
    CURRICULUM_LIST_MESSAGE = "All curriculum fetch successfully."
    CURRICULUM_DELETED_SUCCESSFULLY = "Curriculum deleted successfully."
    CURRICULUM_NOT_FOUND = "Curriculum not found."
    CURRICULUM_DETAIL_MESSAGE = "Curriculum detail fetch successfully."


class ScheduleMessage:
    SCHEDULE_CREATED_SUCCESSFULLY = "Schedule created successfully.",
    SCHEDULE_FETCHED_SUCCESSFULLY = "Schedule fetched successfully."
    SCHEDULE_NOT_FOUND = "Schedule not found."
    SCHEDULE_DELETED_SUCCESSFULLY = "Schedule deleted successfully.",
    SCHEDULE_LIST_MESSAGE = "All schedule fetch successfully."
    SCHEDULE_UPDATED_SUCCESSFULLY = "Teacher schedule updated successfully"


class AttendenceMarkedMessage:
    ATTENDENCE_MARKED_SUCCESSFULLY = "Attendence marked successfully."
