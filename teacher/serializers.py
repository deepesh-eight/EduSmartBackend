import re
from datetime import date, timedelta, datetime
import json

import pytz
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.validators import RegexValidator
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from EduSmart import settings
from authentication.models import TeacherUser, Certificate, TeachersSchedule, TeacherAttendence, DayReview, \
    Notification, TimeTable, StudentUser, Availability, StaffUser, StaffAttendence
from constants import USER_TYPE_CHOICES, GENDER_CHOICES, RELIGION_CHOICES, BLOOD_GROUP_CHOICES, CLASS_CHOICES, \
    SUBJECT_CHOICES, ROLE_CHOICES, ATTENDENCE_CHOICE, EXAME_TYPE_CHOICE
from curriculum.models import Curriculum, Subjects
from student.models import ExmaReportCard, ZoomLink, StudentMaterial, ConnectWithTeacher
from superadmin.models import Announcement


class CertificateSerializer(serializers.ModelSerializer):
    # certificate_file = serializers.SerializerMethodField()
    certificate_name = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ['id', 'certificate_file', 'certificate_name']

    # def get_certificate_file(self, obj):
    #     # Assuming 'image' field stores the file path or URL
    #     if obj.certificate_file:
    #         # Assuming media URL is configured in settings
    #         return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.certificate_file)}'
    #     return None

    def get_certificate_name(self, obj):
        if obj.certificate_file:
            # Assuming media URL is configured in settings
            return str(obj.certificate_file)
        return None


class TeacherUserSignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        ]
    )
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )
    dob = serializers.DateField(required=True)
    image = serializers.ImageField(required=True)
    gender = serializers.CharField(required=True)
    joining_date = serializers.DateField(required=True)
    religion = serializers.CharField(required=True)
    blood_group = serializers.CharField(required=False)
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
    # image = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    class_teacher = serializers.SerializerMethodField()

    class Meta:
        model = TeacherUser
        fields = ['id', 'full_name', 'gender', 'dob', 'blood_group', 'phone', 'address', 'email', 'religion',
                  'role', 'joining_date', 'experience', 'ctc', 'class_subject_section_details', 'image', 'certificates',
                  'highest_qualification', 'class_teacher', 'fcm_token']

    def get_name(self, obj):
        return obj.user.name if hasattr(obj, 'user') else None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

    # def get_image(self, obj):
    #     if obj.image:
    #         if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
    #             return str(obj.image)
    #         else:
    #             return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
    #     return None

    def get_certificates(self, obj):
        # Fetch and serialize certificates associated with the user
        certificates = Certificate.objects.filter(user=obj.user)
        serializer = CertificateSerializer(certificates, many=True)
        return serializer.data

    def get_class_teacher(self, obj):
        if obj.role == 'class teacher':
            class_teacher = obj.class_subject_section_details[0]
            return class_teacher
        return None


class TeacherListSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    phone = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()

    class Meta:
        model = TeacherUser
        fields = ['id', 'full_name', 'phone', 'email', 'class_subject_section_details', 'image',
                  'highest_qualification', 'fcm_token']

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
            raise serializers.ValidationError(
                'Invalid file type. Must be a file object or a string representing a file path.')


class TeacherProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=False)
    phone = serializers.CharField(source='user.phone')
    full_name = serializers.CharField(required=False)
    dob = serializers.DateField(required=False)
    image = ImageFieldStringAndFile(required=False)
    gender = serializers.CharField(required=False)
    joining_date = serializers.DateField(required=False)
    religion = serializers.CharField(required=False)
    blood_group = serializers.CharField(required=False)
    ctc = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    experience = serializers.IntegerField(required=False)
    role = serializers.CharField(required=False)
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
        fields = ['full_name', 'email', 'phone', 'dob', 'image', 'joining_date', 'religion', 'experience', 'role',
                  'address',
                  'ctc', 'blood_group', 'address', 'gender', 'class_subject_section_details', 'certificate_files',
                  'highest_qualification']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        validated_data.pop('email', None)
        validated_data.pop('image', None)
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Handle image separately to avoid re-assigning the URL
        image_data = validated_data.pop('image', None)
        if image_data:
            if hasattr(image_data, 'content_type') or ('blob.core.windows.net' not in image_data):
                instance.image = image_data
            else:
                # If the image_data is a URL, don't update the instance.image
                pass

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
    end_date = serializers.DateField(required=False)
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
    teacher_name = serializers.SerializerMethodField()
    # teacher_id = serializers.SerializerMethodField()
    schedule_data = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = TeachersSchedule
        fields = ['start_date', 'end_date', 'teacher', 'teacher_name', 'schedule_data']

    def get_teacher(self, obj):
        teacher_data = TeacherUser.objects.get(id=obj.teacher_id)
        return teacher_data.id

    def get_teacher_name(self, obj):
        teacher_data = TeacherUser.objects.get(id=obj.teacher_id)
        return teacher_data.full_name

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
    teacher_id = serializers.SerializerMethodField()

    class Meta:
        model = TeachersSchedule
        fields = ['id', 'teacher_id', 'teacher', 'role', 'class_duration', 'total_classes']

    def get_teacher_role(self, teacher_name):
        try:
            teacher = TeacherUser.objects.get(user__email=teacher_name)
            return teacher.role
        except TeacherUser.DoesNotExist:
            return None

    def get_teacher_email(self, obj):
        teacher_data = TeacherUser.objects.get(id=obj.teacher_id)
        return teacher_data.user.email

    def get_teacher_id(self, obj):
        teacher_data = TeacherUser.objects.get(id=obj.teacher_id)
        return teacher_data.id

    def get_teacher(self, obj):
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
        if schedule_data and isinstance(schedule_data, list) and len(schedule_data) > 0:
            return schedule_data[0].get('class_duration', 0)
        return 0


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


# class ScheduleUpdateSerializer(serializers.ModelSerializer):
#     start_date = serializers.DateField(required=False)
#     end_date = serializers.DateField(required=False)
#     teacher = serializers.CharField(required=False)
#     schedule_data = MixedField(required=False)
#
#     class Meta:
#         model = TeachersSchedule
#         fields = ['start_date', 'end_date', 'teacher', 'schedule_data']
#
#     def validate(self, data):
#         start_date = data.get('start_date')
#         end_date = data.get('end_date')
#         if start_date and end_date and end_date < start_date:
#             raise serializers.ValidationError("End date cannot be less than start date.")
#         return data
#
#     def update(self, instance, validated_data):
#         # Update the instance with the validated data
#         instance.start_date = validated_data.get('start_date', instance.start_date)
#         instance.end_date = validated_data.get('end_date', instance.end_date)
#
#         # Fetch the TeacherUser instance based on the provided ID
#         teacher_id = validated_data.get('teacher')
#         if teacher_id:
#             try:
#                 teacher_instance = TeacherUser.objects.get(id=teacher_id)
#                 instance.teacher = teacher_instance
#             except TeacherUser.DoesNotExist:
#                 raise serializers.ValidationError("TeacherUser with ID {} does not exist.".format(teacher_id))
#
#         instance.schedule_data = validated_data.get('schedule_data', instance.schedule_data)
#         instance.save()  # Save the instance after updating
#         return instance  # Return the updated instance

class ScheduleUpdateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    teacher = serializers.CharField(required=False)
    schedule_data = serializers.JSONField(required=False)  # Use JSONField for structured data

    class Meta:
        model = TeachersSchedule
        fields = ['start_date', 'end_date', 'teacher', 'schedule_data']

    def validate_schedule_data(self, value):
        # Ensure schedule_data is either a dictionary or a list
        if not isinstance(value, (dict, list)):
            raise serializers.ValidationError("Invalid format for schedule_data. Must be a list or dictionary.")
        return value

    def update(self, instance, validated_data):
        # Update fields with validated data
        instance.start_date = validated_data.get('start_date', instance.start_date)
        instance.end_date = validated_data.get('end_date', instance.end_date)

        teacher_id = validated_data.get('teacher')
        if teacher_id:
            try:
                teacher_instance = TeacherUser.objects.get(id=teacher_id)
                instance.teacher = teacher_instance
            except TeacherUser.DoesNotExist:
                raise serializers.ValidationError("TeacherUser with ID {} does not exist.".format(teacher_id))

        instance.schedule_data = validated_data.get('schedule_data', instance.schedule_data)
        instance.save()  # Save the instance after updating
        return instance


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
        existing_attendance = TeacherAttendence.objects.filter(teacher=teacher, date=validated_data['date']).exists()
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
        return f"{obj.class_subject_section_details[0].get('class')} class" if obj.role == 'class teacher' else None

    def get_subject(self, obj):
        return obj.class_subject_section_details[0].get("subject") if obj.role == 'class teacher' else None

    def get_section(self, obj):
        return obj.class_subject_section_details[0].get("section") if obj.role == 'class teacher' else None


class TeacherAttendanceFilterListSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    class_teacher = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()

    class Meta:
        model = TeacherAttendence
        fields = ['full_name', 'id', 'class_teacher', 'section', 'subject', 'mark_attendence']

    def get_class_teacher(self, obj):
        return f"{obj.teacher.class_subject_section_details[0].get('class')} class"

    def get_subject(self, obj):
        return obj.teacher.class_subject_section_details[0].get("subject")

    def get_section(self, obj):
        return obj.teacher.class_subject_section_details[0].get("section")

    def get_full_name(self, obj):
        return obj.teacher.full_name

    def get_id(self, obj):
        return obj.teacher.id


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
    # image = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    class_teacher = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()

    # class_subject_section_details = serializers.SerializerMethodField()

    class Meta:
        model = TeacherUser
        fields = ['id', 'full_name', 'gender', 'dob', 'age', 'blood_group', 'phone', 'address', 'email', 'religion',
                  'role', 'joining_date', 'experience', 'ctc', 'class_subject_section_details', 'image', 'certificates',
                  'highest_qualification', 'class_teacher']

    def get_name(self, obj):
        return obj.user.name if hasattr(obj, 'user') else None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

    # def get_image(self, obj):
    #     if obj.image:
    #         if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
    #             return str(obj.image)
    #         else:
    #             return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
    #     return None

    def get_certificates(self, obj):
        # Fetch and serialize certificates associated with the user
        certificates = Certificate.objects.filter(user=obj.user)
        serializer = CertificateUserProfileSerializer(certificates, many=True)
        return serializer.data

    def get_class_teacher(self, obj):
        if obj.role == 'class teacher':
            class_teacher = obj.class_subject_section_details[0]
            return class_teacher
        return None

    def get_age(self, obj):
        if obj.dob:
            today = date.today()
            age = today.year - obj.dob.year - ((today.month, today.day) < (obj.dob.month, obj.dob.day))
            return age
        return None

    # def get_class_subject_section_details(self, obj):
    #     data = []
    #     for detail in obj.class_subject_section_details:
    #         # Find the matching curriculum based on class and section
    #         matching_curriculum = Curriculum.objects.filter(class_name=detail.get('class'),
    #                                                         section=detail.get('section')).first()
    #         if matching_curriculum:
    #             curriculum_data = {
    #                 "class": detail.get('class'),
    #                 "section": detail.get('section'),
    #                 "subject": detail.get('subject'),
    #                 "curriculum": matching_curriculum.exam_board
    #             }
    #             data.append(curriculum_data)
    #     return data


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

            # alter_nate_day = item.get('alternate_day_lecture', '0')
            # select_day = item.get('select_day_lectures', '0')
            # select_days = item.get('select_days', [])
            # if select_day == '1':
            #     lecture_type = f'Selected Day({select_days})'
            # elif alter_nate_day == '1':
            #     lecture_type = f'Alternate Day({select_days})'
            # else:
            #     lecture_type = "Daily"
            item['lecture_type'] = item.get('lecture_type')

            # Remove unnecessary fields
            item.pop('select_day_lecture', None)
            item.pop('select_days', None)
            item.pop('teacher', None)
            item.pop('daily_lecture', None)
            item.pop('alternate_day_lecture', None)

        return representation


class CurriculumSubjectsListerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['primary_subject', 'optional_subject']


class CurriculumSectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUser
        fields = ['section']


class CurriculumClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['select_class']


class DayReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = DayReview
        fields = ['class_name', 'section', 'subject', 'discription', 'curriculum']


class DayReviewDetailSerializer(serializers.ModelSerializer):
    updated_at = serializers.SerializerMethodField()

    class Meta:
        model = DayReview
        fields = ['id', 'class_name', 'section', 'subject', 'discription', 'curriculum', 'updated_at']

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
        extra_kwargs = {
            'description': {'required': False},
        }


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
    curriculum = serializers.CharField(required=True)
    exam_month = serializers.DateField(required=True)
    more_subject = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=255)  # Adjust max_length as needed
        ),
        allow_empty=False
    )

    class Meta:
        model = TimeTable
        fields = ['class_name', 'curriculum', 'class_section', 'exam_type', 'exam_month', 'more_subject']


class TimeTableListSerializer(serializers.ModelSerializer):
    exam_start_date = serializers.SerializerMethodField()
    exam_end_date = serializers.SerializerMethodField()

    class Meta:
        model = TimeTable
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'exam_type', 'exam_start_date', 'exam_end_date']

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
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'exam_type', 'exam_month', 'more_subject']


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
    curriculum = serializers.CharField(required=True)

    class Meta:
        model = ExmaReportCard
        fields = ['class_name', 'curriculum', 'class_section', 'student_name', 'exam_type', 'exam_month',
                  'marks_grades', 'total_marks', 'overall_grades']


class ExamReportListSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    roll_no = serializers.SerializerMethodField()

    class Meta:
        model = ExmaReportCard
        fields = ['id', 'class_name', 'class_section', 'student_name', 'roll_no', 'exam_type']

    def get_student_name(self, obj):
        student = obj.student_name
        student_name = re.search(r'[a-zA-Z\s]+', student).group().strip()
        return student_name

    def get_roll_no(self, obj):
        student = obj.student_name
        roll_no = re.sub(r'\D', '', student)
        return roll_no


class ExamReportCardViewSerializer(serializers.ModelSerializer):
    father_name = serializers.SerializerMethodField()
    mother_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    roll_no = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()

    class Meta:
        model = ExmaReportCard
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'student_name', 'roll_no', 'student', 'exam_type',
                  'exam_month', 'marks_grades', 'total_marks', 'overall_grades', 'father_name', 'mother_name',
                  'teacher_name']

    def get_father_name(self, obj):
        student = obj.student_name
        roll_no = re.sub(r'\D', '', student)
        father_name = StudentUser.objects.get(roll_no=roll_no)
        return father_name.father_name

    def get_mother_name(self, obj):
        student = obj.student_name
        roll_no = re.sub(r'\D', '', student)
        father_name = StudentUser.objects.get(roll_no=roll_no)
        return father_name.mother_name

    def get_teacher_name(self, obj):
        class_name = obj.class_name
        if class_name:
            teacher = TeacherUser.objects.filter(class_subject_section_details__0__class=class_name).first()
            if teacher:
                return teacher.full_name
        return None

    def get_student_name(self, obj):
        student = obj.student_name
        student_name = re.search(r'[a-zA-Z\s]+', student).group().strip()
        return student_name

    def get_roll_no(self, obj):
        student = obj.student_name
        roll_no = re.sub(r'\D', '', student)
        return roll_no

    def get_student(self, obj):
        student = obj.student_name
        return student


class ExamReportcardUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExmaReportCard
        fields = ['class_name', 'class_section', 'student_name', 'exam_type', 'exam_month', 'marks_grades',
                  'total_marks', 'overall_grades']


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
        fields = ['class_name', 'curriculum', 'section', 'subject', 'date', 'start_time', 'end_time', 'zoom_link']


class ZoomLinkListSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = ZoomLink
        fields = ['class_name', 'curriculum', 'section', 'subject', 'date', 'start_time', 'end_time', 'zoom_link']

    def get_start_time(self, obj):
        return obj.start_time.strftime("%I:%M %p")

    def get_end_time(self, obj):
        return obj.end_time.strftime("%I:%M %p")


class StudyMaterialUploadSerializer(serializers.ModelSerializer):
    class_name = serializers.CharField(required=True)
    section = serializers.CharField(required=True)
    curriculum = serializers.CharField(required=True)
    upload_link = serializers.URLField(required=False)
    title = serializers.CharField(required=True)
    discription = serializers.CharField(required=False)
    upload_content = serializers.FileField(required=False)
    content_type = serializers.CharField(required=True)
    subject = serializers.CharField(required=True)

    class Meta:
        model = StudentMaterial
        fields = ['class_name', 'section', 'subject', 'curriculum', 'upload_link', 'title', 'discription',
                  'upload_content', 'content_type']


class StudyMaterialListSerializer(serializers.ModelSerializer):
    # upload_content = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    upload_date = serializers.SerializerMethodField()

    class Meta:
        model = StudentMaterial
        fields = ['id', 'class_name', 'section', 'subject', 'curriculum', 'upload_link', 'title', 'discription',
                  'upload_content', 'content_type', 'teacher', 'upload_date']

    # def get_upload_content(self, obj):
    #     if obj.upload_content:
    #         if obj.upload_content.name.startswith(settings.base_url + settings.MEDIA_URL):
    #             return str(obj.upload_content)
    #         else:
    #             return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.upload_content)}'
    #     return None

    def get_teacher(self, obj):
        teacher = TeacherUser.objects.get(id=obj.teacher_id)
        if teacher:
            return teacher.full_name
        else:
            return None

    def get_upload_date(self, obj):
        return obj.updated_at.date()


class StudyMaterialDetailSerializer(serializers.ModelSerializer):
    # upload_content = serializers.SerializerMethodField()
    class Meta:
        model = StudentMaterial
        fields = ['id', 'class_name', 'section', 'subject', 'curriculum', 'upload_link', 'title', 'discription',
                  'upload_content', 'content_type']

    # def get_upload_content(self, obj):
    #     if obj.upload_content:
    #         if obj.upload_content.name.startswith(settings.base_url + settings.MEDIA_URL):
    #             return str(obj.upload_content)
    #         else:
    #             return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.upload_content)}'
    #     return None


class StudyMaterialUpdateSerializer(serializers.ModelSerializer):
    upload_content = ImageFieldStringAndFile()

    class Meta:
        model = StudentMaterial
        fields = ['id', 'class_name', 'section', 'subject', 'curriculum', 'upload_link', 'title', 'discription',
                  'upload_content', 'content_type']


class SectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUser
        fields = ['section']


class SubjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['primary_subject', 'optional_subject']


class CustomTimeField(serializers.TimeField):
    def to_internal_value(self, value):
        try:
            # Convert 12-hour time format to 24-hour time format
            if isinstance(value, str):
                value = datetime.strptime(value, '%I:%M %p').strftime('%H:%M:%S')
        except ValueError:
            raise serializers.ValidationError('Time has wrong format. Use hh:mm[:ss[.uuuuuu]] instead.')
        return super().to_internal_value(value)


class AvailabilityCreateSerializer(serializers.ModelSerializer):
    start_time = CustomTimeField(required=True)
    end_time = CustomTimeField(required=False)

    class Meta:
        model = Availability
        fields = ['start_time', 'end_time']


class AvailabilityGetSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField(required=False)
    end_time = serializers.SerializerMethodField(required=False)

    class Meta:
        model = Availability
        fields = ['start_time', 'end_time']

    def get_start_time(self, obj):
        start_time = str(obj.start_time)
        if start_time:
            return datetime.strptime(start_time, '%H:%M:%S').strftime('%I:%M %p')

    def get_end_time(self, obj):
        end_time = str(obj.end_time)
        if end_time:
            return datetime.strptime(end_time, '%H:%M:%S').strftime('%I:%M %p')


class ChatRequestMessageSerializer(serializers.ModelSerializer):
    student_image = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()

    class Meta:
        model = ConnectWithTeacher
        fields = ['id', 'student_image', 'student_name', 'start_time', 'status']

    def get_student_name(self, obj):
        student = StudentUser.objects.get(id=obj.student.id)
        if student:
            return student.name
        else:
            None

    def get_student_image(self, obj):
        student = StudentUser.objects.get(id=obj.student.id)
        if student:
            if student.image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(student.image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(student.image)}'
        else:
            None

    def get_start_time(self, obj):
        start_time = str(obj.start_time)
        if start_time:
            return datetime.strptime(start_time, '%H:%M:%S').strftime('%I:%M %p')


class TeacherChatHistorySerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()

    class Meta:
        model = ConnectWithTeacher
        fields = ['id', 'student_id', 'student_name', 'class_name', 'section']

    def get_student_name(self, obj):
        student = StudentUser.objects.get(id=obj.student.id)
        if student:
            return student.name
        else:
            None

    def get_student_id(self, obj):
        student = StudentUser.objects.get(id=obj.student.id)
        if student:
            return student.id
        else:
            None


class StudentChatRequestMessageSerializer(serializers.ModelSerializer):
    teacher_image = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()

    class Meta:
        model = ConnectWithTeacher
        fields = ['id', 'teacher_image', 'teacher_name', 'start_time', 'status']

    def get_teacher_name(self, obj):
        teacher = TeacherUser.objects.get(id=obj.teacher.id)
        if teacher:
            return teacher.full_name
        else:
            None

    def get_teacher_image(self, obj):
        teacher = TeacherUser.objects.get(id=obj.teacher.id)
        if teacher:
            if teacher.image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(teacher.image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(teacher.image)}'
        else:
            None

    def get_start_time(self, obj):
        start_time = str(obj.start_time)
        if start_time:
            return datetime.strptime(start_time, '%H:%M:%S').strftime('%I:%M %p')


class TeacherListBySectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherUser
        fields = ['id', 'full_name']


class TeacherAttendanceCreateSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField(required=False)

    class Meta:
        model = TeacherAttendence
        fields = ['id', 'date', 'mark_attendence']

    def validate(self, data):
        if 'date' in data:
            try:
                # Attempt to parse the date string
                data['date'] = serializers.DateField().to_internal_value(data['date'])
            except serializers.ValidationError:
                raise serializers.ValidationError({"date": ["Date must be in YYYY-MM-DD format"]})
        return data


class StaffListBySectionSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = StaffUser
        fields = ['id', 'full_name']

    def get_full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'


class StaffAttendanceCreateSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField(required=False)

    class Meta:
        model = StaffAttendence
        fields = ['id', 'date', 'mark_attendence']

    def validate(self, data):
        if 'date' in data:
            try:
                # Attempt to parse the date string
                data['date'] = serializers.DateField().to_internal_value(data['date'])
            except serializers.ValidationError:
                raise serializers.ValidationError({"date": ["Date must be in YYYY-MM-DD format"]})
        return data
