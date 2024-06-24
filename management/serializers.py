import re

from rest_framework import serializers

from EduSmart import settings
from authentication.models import StaffUser, Certificate, TimeTable, TeacherUser, StudentUser
from curriculum.models import Curriculum
from student.models import ExmaReportCard
from superadmin.models import SchoolProfile
from teacher.serializers import CertificateSerializer


class ManagementProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    phone = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    school_id = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    curriculum = serializers.SerializerMethodField()
    school_website = serializers.SerializerMethodField()
    school_address = serializers.SerializerMethodField()
    school_about = serializers.SerializerMethodField()
    super_admin_mail = serializers.SerializerMethodField()

    class Meta:
        model = StaffUser
        fields = ['id', 'first_name', 'last_name', 'role', 'phone', 'email', 'image', 'dob', 'gender', 'religion',
                  'blood_group', 'address', 'joining_date',
                  'ctc', 'certificates', 'experience', 'highest_qualification', 'school_id', 'school_name', 'school_website',
                  'school_address', 'school_about', 'curriculum', 'super_admin_mail']

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None

    def get_image(self, obj):
        if obj.image:
            if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
        return None

    def get_certificates(self, obj):
        # Fetch and serialize certificates associated with the user
        certificates = Certificate.objects.filter(user=obj.user)
        serializer = CertificateSerializer(certificates, many=True)
        return serializer.data

    def get_super_admin_mail(self, obj):
        return "support@edusmartai.com"

    def get_school_id(self, obj):
        return obj.user.school_id

    def get_school_name(self, obj):
        school = SchoolProfile.objects.get(school_id=obj.user.school_id)
        if school:
            return school.school_name
        else:
            None

    def get_school_website(self, obj):
        school = SchoolProfile.objects.get(school_id=obj.user.school_id)
        if school:
            return school.school_website
        else:
            None

    def get_school_address(self, obj):
        school = SchoolProfile.objects.get(school_id=obj.user.school_id)
        if school:
            return school.address
        else:
            None

    def get_school_about(self, obj):
        school = SchoolProfile.objects.get(school_id=obj.user.school_id)
        if school:
            return school.description
        else:
            None

    def get_curriculum(self, obj):
        curriculum = Curriculum.objects.filter(school_id=obj.user.school_id)
        data = []
        if curriculum:
            for curriculum_data in curriculum:
                data.append(curriculum_data.curriculum_name)
            return set(data)
        else:
            None


class TimeTableSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    exam_month = serializers.SerializerMethodField()

    class Meta:
        model = TimeTable
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'exam_type', 'start_date', 'exam_month']

    def get_start_date(self, obj):
        more_subjects = obj.more_subject
        if more_subjects:
            exam_dates = [subject['date'] for subject in more_subjects]
            return min(exam_dates)
        return None

    def get_exam_month(self, obj):
        return obj.exam_month.strftime("%B")


class TimeTableDetailViewSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    class Meta:
        model = TimeTable
        fields = ['id', 'teacher', 'class_name', 'curriculum', 'class_section', 'exam_type', 'exam_month', 'more_subject']

    def get_teacher(self, obj):
        teacher = TeacherUser.objects.get(id=obj.teacher_id)
        if teacher:
            return teacher.full_name
        else:
            return None


class ExamReportCardSerializer(serializers.ModelSerializer):
    upload_date = serializers.SerializerMethodField()
    exam_month = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    roll_no = serializers.SerializerMethodField()
    class Meta:
        model = ExmaReportCard
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'exam_type', 'exam_month', 'upload_date', 'student_name', 'roll_no']

    def get_upload_date(self, obj):
        return obj.updated_at.date()

    def get_exam_month(self, obj):
        return obj.exam_month.strftime("%B")

    def get_student_name(self, obj):
        name, _ = self.split_student_data(obj.student_name)
        return name

    def get_roll_no(self, obj):
        _, roll_no = self.split_student_data(obj.student_name)
        return roll_no

    def split_student_data(self, student_data):
        pattern = r'^(.*?)-(.*?)$'
        match = re.match(pattern, student_data)
        if match:
            student_name = match.group(1).strip()
            roll_no = match.group(2).strip()
            return student_name, roll_no
        else:
            raise serializers.ValidationError("Input format is incorrect. Expected format: 'name-roll_no'.")


class StudentReportCardSerializer(serializers.ModelSerializer):
    # father_name = serializers.SerializerMethodField()
    # mother_name = serializers.SerializerMethodField()
    # teacher_name = serializers.SerializerMethodField()
    # student_id = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    roll_no = serializers.SerializerMethodField()

    class Meta:
        model = ExmaReportCard
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'roll_no', 'student_name', 'exam_type',
                 'marks_grades', 'total_marks', 'overall_grades']

    # def get_student_id(self, obj):
    #     student = obj.student_name
    #     roll_no = re.sub(r'\D', '', student)
    #     student_id = StudentUser.objects.get(roll_no=roll_no)
    #     return student_id.id

    def get_upload_date(self, obj):
        return obj.updated_at.date()

    def get_exam_month(self, obj):
        return obj.exam_month.strftime("%B")

    def get_student_name(self, obj):
        name, _ = self.split_student_data(obj.student_name)
        return name

    def get_roll_no(self, obj):
        _, roll_no = self.split_student_data(obj.student_name)
        return roll_no

    def split_student_data(self, student_data):
        pattern = r'^(.*?)-(.*?)$'
        match = re.match(pattern, student_data)
        if match:
            student_name = match.group(1).strip()
            roll_no = match.group(2).strip()
            return student_name, roll_no
        else:
            raise serializers.ValidationError("Input format is incorrect. Expected format: 'name-roll_no'.")

    # def get_father_name(self, obj):
    #     roll_no = self.get_roll_no(obj)
    #     father_name = StudentUser.objects.get(roll_no=roll_no)
    #     return father_name.father_name
    #
    # def get_mother_name(self, obj):
    #     roll_no = self.get_roll_no(obj)
    #     mother_name = StudentUser.objects.get(roll_no=roll_no)
    #     return mother_name.mother_name
    #
    # def get_teacher_name(self, obj):
    #     class_name = obj.class_name
    #     if class_name:
    #         teacher = TeacherUser.objects.filter(class_subject_section_details__0__class=class_name).first()
    #         if teacher:
    #             return teacher.full_name
    #     return None