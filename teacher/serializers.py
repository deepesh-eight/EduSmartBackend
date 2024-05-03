from datetime import date, timedelta, datetime
import json

import pytz
from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from EduSmart import settings
from authentication.models import TeacherUser, Certificate, TeachersSchedule, TeacherAttendence, DayReview, \
    Notification, TimeTable, StudentUser
from constants import USER_TYPE_CHOICES, GENDER_CHOICES, RELIGION_CHOICES, BLOOD_GROUP_CHOICES, CLASS_CHOICES, \
    SUBJECT_CHOICES, ROLE_CHOICES, ATTENDENCE_CHOICE, EXAME_TYPE_CHOICE
from curriculum.models import Curriculum
from student.models import ExmaReportCard, ZoomLink, StudentMaterial
from superadmin.models import Announcement


class CertificateSerializer(serializers.ModelSerializer):
    certificate_file = serializers.SerializerMethodField()
    class Meta:
        model = Certificate
        fields = ['certificate_file']

    def get_certificate_file(self, obj):
        # Assuming 'image' field stores the file path or URL
        if obj.certificate_file:
            # Assuming media URL is configured in settings
            return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.certificate_file)}'
        return None


class TeacherUserSignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )
    dob = serializers.DateField(required=True)
    image = serializers.ImageField(required=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True)
    joining_date = serializers.DateField(required=True)
    religion = serializers.ChoiceField(choices=RELIGION_CHOICES, required=True)
    blood_group = serializers.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False)
    ctc = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    experience = serializers.IntegerField(required=False)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=True)
    address = serializers.CharField(max_length=255, required=False)
    class_subject_section_details = serializers.CharField()
    highest_qualification = serializers.CharField(max_length=255)
    certificate_files = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        try:
            class_subject_section_details_str = json.loads(
                data.get('class_subject_section_details', '[]'))  # Parse string input as JSON
            ret['class_subject_section_details'] = class_subject_section_details_str
        except json.JSONDecodeError:
            raise serializers.ValidationError({'class_subject_section_details': 'Invalid JSON format'})

        return ret

    def validate_certificate_files(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("Can't add more than 5 certificates.")

        for cert_file in value:
            if cert_file.size > 1048576:  # 1 MB
                raise serializers.ValidationError('Uploaded certificate size cannot exceed 1 MB.')

            try:
                cert_file.open()  # Ensure the file is open before further processing
                # Here you can perform additional validation if needed
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))

        return value

class TeacherDetailSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    class_teacher = serializers.SerializerMethodField()

    class Meta:
        model = TeacherUser
        fields = ['id', 'full_name', 'gender', 'dob', 'blood_group', 'phone', 'address', 'email', 'religion',
                  'role', 'joining_date', 'experience', 'ctc', 'class_subject_section_details', 'image', 'certificates', 'highest_qualification', 'class_teacher']

    def get_name(self, obj):
        return obj.user.name if hasattr(obj, 'user') else None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

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

    def get_class_teacher(self, obj):
        if obj.role == 'class_teacher':
            class_teacher = obj.class_subject_section_details[0]
            return class_teacher
        return None


class TeacherListSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    phone = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = TeacherUser
        fields = ['id', 'full_name', 'phone', 'email', 'class_subject_section_details', 'image', 'highest_qualification']

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

    def get_subject(self, obj):
        subjects_str = obj.subject
        if subjects_str:
            return eval(subjects_str)
        return []

    def get_image(self, obj):
        if obj.image:
            if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
        return None


class ImageFieldStringAndFile(serializers.Field):
    def to_representation(self, value):
        if value:
            # Assuming value is a file path string
            return value.url if hasattr(value, 'url') else value
        return None

    def to_internal_value(self, data):
        # If data is a file object, return it as is
        if hasattr(data, 'content_type'):
            return data
        # If data is a string (file path), return it as is
        elif isinstance(data, str):
            return data
        else:
            raise serializers.ValidationError('Invalid file type. Must be a file object or a string representing a file path.')

class TeacherProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email',required=False)
    phone = serializers.CharField(source='user.phone')
    full_name = serializers.CharField(required=False)
    dob = serializers.DateField(required=False)
    image = ImageFieldStringAndFile(required=False)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=False)
    joining_date = serializers.DateField(required=False)
    religion = serializers.ChoiceField(choices=RELIGION_CHOICES, required=False)
    blood_group = serializers.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False)
    ctc = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    experience = serializers.IntegerField(required=False)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=False)
    address = serializers.CharField(max_length=255, required=False)
    class_subject_section_details = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=100)  # Adjust max_length as needed
        ),
        allow_empty=True
    )
    certificate_files = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )


    class Meta:
        model = TeacherUser
        fields = ['full_name', 'email', 'phone', 'dob', 'image', 'joining_date', 'religion', 'experience', 'role', 'address',
                  'ctc', 'blood_group', 'address', 'gender', 'class_subject_section_details','certificate_files', 'highest_qualification']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        validated_data.pop('email', None)
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        return super().update(instance, validated_data)

    def validate_certificate_files(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("Can't add more than 5 certificates.")

        for cert_file in value:
            if cert_file.size > 1048576:  # 1 MB
                raise serializers.ValidationError('Uploaded certificate size cannot exceed 1 MB.')

            try:
                cert_file.open()  # Ensure the file is open before further processing
                # Here you can perform additional validation if needed
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))

        return value


class ScheduleCreateSerializer(serializers.Serializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    teacher = serializers.CharField(required=True)
    schedule_data = serializers.ListField(
        child=serializers.CharField(),
        required=True
    )

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        try:
            schedule_str = json.loads(
                data.get('schedule_data', '[]'))  # Parse string input as JSON
            ret['schedule_data'] = schedule_str
        except json.JSONDecodeError:
            raise serializers.ValidationError({'schedule_data': 'Invalid JSON format'})

        return ret

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError("End date cannot be less than start date.")
        return data


class ScheduleDetailSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    teacher_id = serializers.SerializerMethodField()
    schedule_data = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = TeachersSchedule
        fields = ['start_date', 'end_date', 'teacher', 'teacher_id', 'schedule_data']

    def get_teacher(self, obj):
        teacher_data = TeacherUser.objects.get(id=obj.teacher_id)
        return teacher_data.full_name

    def get_teacher_id(self, obj):
        teacher_data = TeacherUser.objects.get(id=obj.teacher_id)
        return teacher_data.id


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        schedule_data = representation.get('schedule_data', [])

        # Iterate through each schedule item and modify its representation
        for item in schedule_data:
            # Add class_timing_duration field
            class_timing = item.get('class_timing', '')
            class_duration = item.get('class_duration', '')
            select_days = item.get('select_days', [])
            class_teach = item.get('class', '')
            class_teach = item.get('lecture_type', '')

            # # Add lecture_type field
            # alter_nate_day = item.get('alternate_day_lecture', '0')
            # select_day = item.get('select_day_lectures', '0')
            # select_days = item.get('select_days', [])
            # if select_day == '1':
            #     lecture_type = f'Selected Day({select_days})'
            # elif alter_nate_day == '1':
            #     lecture_type = f'Alternate Day({select_days})'
            # else:
            #     lecture_type = "Daily"
            # item['lecture_type'] = lecture_type

            # Remove unnecessary fields
            item.pop('select_day_lecture', None)
            item.pop('teacher', None)
            item.pop('daily_lecture', None)
            item.pop('alternate_day_lecture', None)

        return representation


class ScheduleListSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    class_duration = serializers.SerializerMethodField()
    total_classes = serializers.SerializerMethodField()
    class Meta:
        model = TeachersSchedule
        fields = ['id', 'teacher', 'role', 'class_duration', 'total_classes']

    def get_teacher_role(self, teacher_name):
        try:
            teacher = TeacherUser.objects.get(user__email=teacher_name)
            return teacher.role  # Assuming 'role' is the field you want to retrieve
        except TeacherUser.DoesNotExist:
            return None

    def get_teacher_email(self, obj):
        teacher_data = TeacherUser.objects.get(id=obj.teacher_id)
        return teacher_data.user.email

    def get_teacher(self,obj):
        teacher_data = TeacherUser.objects.get(id=obj.teacher_id)
        return teacher_data.full_name

    def get_role(self, obj):
        teacher_email = self.get_teacher_email(obj)
        return self.get_teacher_role(teacher_email) if teacher_email else None

    def get_total_classes(self, obj):
        schedule_data = obj.schedule_data
        return len(schedule_data) if schedule_data else 0

    def get_class_duration(self, obj):
        schedule_data = obj.schedule_data
        return schedule_data[0]['class_duration'] if schedule_data else 0

class MixedField(serializers.Field):
    """
    A custom field to handle mixed data types (string or list).
    """

    def to_internal_value(self, data):
        if isinstance(data, list):
            return data
        elif isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                raise serializers.ValidationError("Invalid JSON format.")
        else:
            raise serializers.ValidationError("Invalid input format.")

    def to_representation(self, value):
        return value


class ScheduleUpdateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    teacher = serializers.CharField(required=True)
    schedule_data = MixedField(required=True)

    class Meta:
        model = TeachersSchedule
        fields = ['start_date', 'end_date', 'teacher', 'schedule_data']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError("End date cannot be less than start date.")
        return data

    def update(self, instance, validated_data):
        # Update the instance with the validated data
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)

        # Fetch the TeacherUser instance based on the provided ID
        teacher_id = validated_data.get('teacher')
        if teacher_id:
            try:
                teacher_instance = TeacherUser.objects.get(id=teacher_id)
                instance.teacher = teacher_instance
            except TeacherUser.DoesNotExist:
                raise serializers.ValidationError("TeacherUser with ID {} does not exist.".format(teacher_id))

        instance.schedule_data = validated_data.get('schedule_data', instance.schedule_data)
        instance.save()  # Save the instance after updating
        return instance  # Return the updated instance


class TeacherAttendanceSerializer(serializers.ModelSerializer):
    teacher = serializers.CharField(required=True)
    mark_attendence = serializers.ChoiceField(choices=ATTENDENCE_CHOICE, required=True)

    class Meta:
        model = TeacherAttendence
        fields = ['teacher', 'mark_attendence']

    def create(self, validated_data):
        validated_data['date'] = date.today()
        teacher_id = validated_data.pop('teacher')
        try:
            teacher = TeacherUser.objects.get(id=teacher_id)
        except TeacherUser.DoesNotExist:
            raise serializers.ValidationError("Invalid teacher ID.")

        # Check if attendance already marked for the user and today's date
        existing_attendance = TeacherAttendence.objects.filter(teacher=teacher,date=validated_data['date']).exists()
        if existing_attendance:
            raise serializers.ValidationError("Attendance already marked for this teacher today.")

        # Use the retrieved teacher object to create the attendance record
        teacher_attendance = TeacherAttendence.objects.create(teacher=teacher, **validated_data)
        return teacher_attendance


class TeacherAttendanceDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = TeacherAttendence
        fields = ['date', 'mark_attendence']


class TeacherAttendanceListSerializer(serializers.ModelSerializer):
    class_teacher = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()

    class Meta:
        model = TeacherUser
        fields = ['full_name', 'id', 'class_teacher', 'subject', 'section']

    def get_class_teacher(self, obj):
        return f"{obj.class_subject_section_details[0].get('class')} class" if obj.role == 'class_teacher' else None

    def get_subject(self, obj):
        return obj.class_subject_section_details[0].get("subject") if obj.role == 'class_teacher' else None

    def get_section(self, obj):
        return obj.class_subject_section_details[0].get("section") if obj.role == 'class_teacher' else None


class CertificateUserProfileSerializer(serializers.ModelSerializer):
    certificate_file = serializers.SerializerMethodField()
    certificate_name = serializers.SerializerMethodField()
    class Meta:
        model = Certificate
        fields = ['certificate_file', 'certificate_name']

    def get_certificate_file(self, obj):
        # Assuming 'image' field stores the file path or URL
        if obj.certificate_file:
            # Assuming media URL is configured in settings
            return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.certificate_file)}'
        return None

    def get_certificate_name(self, obj):
        if obj.certificate_file:
            # Assuming media URL is configured in settings
            return str(obj.certificate_file)
        return None


class TeacherUserProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    class_teacher = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    class_subject_section_details = serializers.SerializerMethodField()

    class Meta:
        model = TeacherUser
        fields = ['id', 'full_name', 'gender', 'dob', 'age', 'blood_group', 'phone', 'address', 'email', 'religion',
                  'role', 'joining_date', 'experience', 'ctc', 'class_subject_section_details', 'image', 'certificates', 'highest_qualification', 'class_teacher']

    def get_name(self, obj):
        return obj.user.name if hasattr(obj, 'user') else None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

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
        serializer = CertificateUserProfileSerializer(certificates, many=True)
        return serializer.data

    def get_class_teacher(self, obj):
        if obj.role == 'class_teacher':
            class_teacher = obj.class_subject_section_details[0]
            return class_teacher
        return None

    def get_age(self, obj):
        if obj.dob:
            today = date.today()
            age = today.year - obj.dob.year - ((today.month, today.day) < (obj.dob.month, obj.dob.day))
            return age
        return None

    def get_class_subject_section_details(self, obj):
        data = []
        for detail in obj.class_subject_section_details:
            # Find the matching curriculum based on class and section
            matching_curriculum = Curriculum.objects.filter(class_name=detail.get('class'),
                                                            section=detail.get('section')).first()
            if matching_curriculum:
                curriculum_data = {
                    "class": detail.get('class'),
                    "section": detail.get('section'),
                    "subject": detail.get('subject'),
                    "curriculum": matching_curriculum.exam_board
                }
                data.append(curriculum_data)
        return data


class TeacherUserScheduleSerializer(serializers.ModelSerializer):
    schedule_date = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    schedule_data = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = TeachersSchedule
        fields = ['schedule_date', 'teacher', 'schedule_data']

    def get_teacher(self, obj):
        teacher_data = TeacherUser.objects.get(id=obj.teacher.id)
        return teacher_data.full_name

    def get_schedule_date(self, obj):
        return f'{obj.start_date} to {obj.end_date}'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        schedule_data = representation.get('schedule_data', [])

        # Iterate through each schedule item and modify its representation
        for item in schedule_data:

            class_timing = item.get('class_timing', '')
            if ':' in class_timing and ' ' in class_timing:
                # If already in the desired format, keep it unchanged
                pass
            else:
                # If not in the desired format, convert it
                class_timing = datetime.strptime(class_timing, '%I:%M%p').strftime('%I:%M %p')
                item['class_timing'] = class_timing

            class_duration = item.get('class_duration', '')

            if class_timing and class_duration:
                # Extract hours and minutes from class_duration
                duration_minutes = int(class_duration.split()[0])

                # Convert class_timing to datetime object
                start_time = datetime.strptime(class_timing, '%I:%M %p')

                # Calculate end time
                end_time = start_time + timedelta(minutes=duration_minutes)

                # Format the time range
                time_range = f"{class_timing}-{end_time.strftime('%I:%M %p')}"
                item['class_time_range'] = time_range
            else:
                item['class_time_range'] = None

            # Modify lecture_type field as before
            alter_nate_day = item.get('alternate_day_lecture', '0')
            select_day = item.get('select_day_lectures', '0')
            select_days = item.get('select_days', [])
            if select_day == '1':
                lecture_type = f'Selected Day({select_days})'
            elif alter_nate_day == '1':
                lecture_type = f'Alternate Day({select_days})'
            else:
                lecture_type = "Daily"
            item['lecture_type'] = lecture_type

            # Remove unnecessary fields
            item.pop('select_day_lecture', None)
            item.pop('select_days', None)
            item.pop('teacher', None)
            item.pop('daily_lecture', None)
            item.pop('alternate_day_lecture', None)

        return representation


class CurriculumTeacherListerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['id', 'subject_name_code', 'class_name', 'section']


class DayReviewSerializer(serializers.ModelSerializer):
    school_id = serializers.CharField(required=False)

    class Meta:
        model = DayReview
        fields = ['class_name', 'section', 'subject', 'discription', 'school_id']


class DayReviewDetailSerializer(serializers.ModelSerializer):
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = DayReview
        fields = ['id', 'class_name', 'section', 'subject', 'discription', 'school_id', 'updated_at']

    def get_updated_at(self, obj):
        cleaned_date_str = str(obj.updated_at).split('.')[0]
        date_obj = datetime.strptime(cleaned_date_str, "%Y-%m-%d %H:%M:%S")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        return formatted_date


class TeacherUserAttendanceListSerializer(serializers.ModelSerializer):
    day = serializers.SerializerMethodField()

    class Meta:
        model = TeacherAttendence
        fields = ['date', 'mark_attendence', 'day']

    def get_day(self, obj):
        return obj.date.strftime('%A')


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['title', 'description', 'date_time', 'sender', 'type', 'is_read', 'reciver_id', 'class_id']


class NotificationListSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    class Meta:
        model = Notification
        fields = ['title', 'description', 'date', 'time', 'sender', 'type', 'is_read', 'reciver_id', 'class_id']


    def get_date(self, obj):
        ist = pytz.timezone('Asia/Kolkata')
        date_time_ist = obj.date_time.astimezone(ist)
        return date_time_ist.strftime("%Y-%m-%d")

    def get_time(self, obj):
        ist = pytz.timezone('Asia/Kolkata')
        date_time_ist = obj.date_time.astimezone(ist)
        return date_time_ist.strftime("%H:%M:%S")


class AnnouncementCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Announcement
        fields = ['creator_name', 'date_time', 'announcement_title', 'description']


class AnnouncementListSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()
    class Meta:
        model = Announcement
        fields = ['id', 'creator_name', 'date', 'time', 'announcement_title', 'description', 'role']

    def get_date(self, obj):
        ist = pytz.timezone('Asia/Kolkata')
        date_time_ist = obj.date_time.astimezone(ist)
        return date_time_ist.strftime("%Y-%m-%d")

    def get_time(self, obj):
        ist = pytz.timezone('Asia/Kolkata')
        date_time_ist = obj.date_time.astimezone(ist)
        return date_time_ist.strftime("%H:%M:%S")


class CreateTimeTableSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(required=True)
    class_section = serializers.CharField(required=True)
    exam_type = serializers.ChoiceField(
        choices=EXAME_TYPE_CHOICE
    )
    exam_month = serializers.DateField(required=True)
    more_subject = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=255)  # Adjust max_length as needed
        ),
        allow_empty=False
    )

    class Meta:
        model = TimeTable
        fields = ['class_name', 'class_section', 'exam_type', 'exam_month', 'more_subject']


class TimeTableListSerializer(serializers.ModelSerializer):
    exam_start_date = serializers.SerializerMethodField()
    exam_end_date = serializers.SerializerMethodField()
    class Meta:
        model = TimeTable
        fields = ['id', 'class_name', 'class_section', 'exam_type', 'exam_start_date', 'exam_end_date']

    def get_exam_start_date(self, obj):
        more_subjects = obj.more_subject
        if more_subjects:
            exam_dates = [subject['date'] for subject in more_subjects]
            return min(exam_dates)
        return None
    #
    def get_exam_end_date(self, obj):
        more_subjects = obj.more_subject
        if more_subjects:
            exam_dates = [subject['date'] for subject in more_subjects]
            return max(exam_dates)
        return None


class TimeTableDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeTable
        fields = ['id', 'class_name', 'class_section', 'exam_type', 'exam_month', 'more_subject']


class TimeTableUpdateSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(required=True)
    class_section = serializers.CharField(required=True)
    exam_type = serializers.ChoiceField(
        choices=EXAME_TYPE_CHOICE
    )
    exam_month = serializers.DateField(required=True)
    more_subject = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=255)  # Adjust max_length as needed
        ),
        allow_empty=False
    )

    class Meta:
        model = TimeTable
        fields = ['class_name', 'class_section', 'exam_type', 'exam_month', 'more_subject']


class ExamReportCreateSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(required=True)
    class_section = serializers.CharField(required=True)
    student_name = serializers.CharField(required=True)
    roll_no = serializers.CharField(required=True)
    exam_type = serializers.CharField(required=True)
    exam_month = serializers.DateField(required=True)
    total_marks = serializers.CharField(required=True)
    overall_grades = serializers.CharField(required=True)
    marks_grades = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=255)  # Adjust max_length as needed
        ),
        allow_empty=False
    )

    class Meta:
        model = ExmaReportCard
        fields = ['class_name', 'class_section', 'student_name', 'roll_no', 'exam_type', 'exam_month', 'marks_grades', 'total_marks', 'overall_grades']


class ExamReportListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExmaReportCard
        fields = ['id', 'class_name', 'class_section', 'student_name', 'roll_no', 'exam_type']


class ExamReportCardViewSerializer(serializers.ModelSerializer):
    father_name = serializers.SerializerMethodField()
    mother_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = ExmaReportCard
        fields = ['id', 'class_name', 'class_section', 'student_name', 'roll_no', 'exam_type', 'exam_month', 'marks_grades', 'total_marks', 'overall_grades', 'father_name', 'mother_name', 'teacher_name']

    def get_father_name(self, obj):
        father_name = StudentUser.objects.get(roll_no=obj.roll_no)
        return father_name.father_name

    def get_mother_name(self, obj):
        father_name = StudentUser.objects.get(roll_no=obj.roll_no)
        return father_name.mother_name

    def get_teacher_name(self, obj):
        class_name = obj.class_name
        if class_name:
            teacher = TeacherUser.objects.filter(class_subject_section_details__0__class=class_name).first()
            if teacher:
                return teacher.full_name
        return None


class ExamReportcardUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExmaReportCard
        fields = ['class_name', 'class_section', 'student_name', 'roll_no', 'exam_type', 'exam_month', 'marks_grades', 'total_marks', 'overall_grades']


class ZoomLinkCreateSerializer(serializers.ModelSerializer):
    zoom_link = serializers.URLField(max_length=500)

    def to_internal_value(self, data):
        mutable_data = data.copy()
        for field in ['start_time', 'end_time']:  # Loop through start_time and end_time fields
            if field in mutable_data:
                try:
                    # Parse the time and convert to 24-hour format
                    time_obj = datetime.strptime(mutable_data[field], "%I:%M %p")
                    mutable_data[field] = time_obj.strftime("%H:%M")
                except ValueError:
                    raise serializers.ValidationError(
                        f"Invalid {field} format. Please provide time in 12-hour format (hh:mm AM/PM).")

        return super().to_internal_value(mutable_data)

    class Meta:
        model = ZoomLink
        fields = ['class_name', 'section', 'subject', 'date', 'start_time', 'end_time', 'zoom_link']


class ZoomLinkListSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    class Meta:
        model = ZoomLink
        fields = ['class_name', 'section', 'subject', 'date', 'start_time', 'end_time', 'zoom_link']

    def get_start_time(self, obj):
        return obj.start_time.strftime("%I:%M %p")

    def get_end_time(self, obj):
        return obj.end_time.strftime("%I:%M %p")


class StudyMaterialUploadSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(required=True)
    subject = serializers.CharField(required=True)
    curriculum = serializers.CharField(required=True)
    upload_link = serializers.URLField(required=False)
    title = serializers.CharField(required=True)
    discription = serializers.CharField(required=False)
    upload_content = serializers.FileField(required=False)

    class Meta:
        model = StudentMaterial
        fields = ['class_name', 'subject', 'curriculum', 'upload_link', 'title', 'discription', 'upload_content']


class StudyMaterialListSerializer(serializers.ModelSerializer):
    upload_content = serializers.SerializerMethodField()
    class Meta:
        model = StudentMaterial
        fields = ['id', 'class_name', 'subject', 'curriculum', 'upload_link', 'title', 'discription', 'upload_content']

    def get_upload_content(self, obj):
        if obj.upload_content:
            if obj.upload_content.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.upload_content)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.upload_content)}'
        return None


class StudyMaterialDetailSerializer(serializers.ModelSerializer):
    upload_content = serializers.SerializerMethodField()
    class Meta:
        model = StudentMaterial
        fields = ['id', 'class_name', 'subject', 'curriculum', 'upload_link', 'title', 'discription', 'upload_content']

    def get_upload_content(self, obj):
        if obj.upload_content:
            if obj.upload_content.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.upload_content)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.upload_content)}'
        return None


class SectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUser
        fields = ['section']