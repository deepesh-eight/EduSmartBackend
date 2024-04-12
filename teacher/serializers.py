import json

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from EduSmart import settings
from authentication.models import TeacherUser, Certificate, TeachersSchedule
from constants import USER_TYPE_CHOICES, GENDER_CHOICES, RELIGION_CHOICES, BLOOD_GROUP_CHOICES, CLASS_CHOICES, \
    SUBJECT_CHOICES, ROLE_CHOICES


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

    class Meta:
        model = TeacherUser
        fields = ['id', 'full_name', 'gender', 'dob', 'blood_group', 'phone', 'address', 'email', 'religion',
                  'role', 'joining_date', 'experience', 'ctc', 'class_subject_section_details', 'image', 'certificates', 'highest_qualification']

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

class ScheduleCreateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    schedule_data = serializers.CharField(required=True)

    class Meta:
        model = TeachersSchedule
        fields = ['start_date', 'end_date', 'schedule_data']

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
    schedule_date = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    schedule_data = serializers.ListField(child=serializers.DictField(), required=False)

    class Meta:
        model = TeachersSchedule
        fields = ['schedule_date', 'teacher', 'schedule_data']

    def get_teacher(self, obj):
        schedule_data = obj.schedule_data
        if schedule_data:
            teacher_name = schedule_data[0]['teacher'] if schedule_data else None
            return teacher_name
        return None

    def get_schedule_date(self, obj):
        return f'{obj.start_date} to {obj.end_date}'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        schedule_data = representation.get('schedule_data', [])

        # Iterate through each schedule item and modify its representation
        for item in schedule_data:
            # Add class_timing_duration field
            class_timing = item.get('class_timing', '')
            class_duration = item.get('class_duration', '')
            item['class_timing_duration'] = f"{class_timing}|({class_duration})"

            # Add lecture_type field
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
            item.pop('class_timing', None)
            item.pop('class_duration', None)
            item.pop('select_day_lecture', None)
            item.pop('select_days', None)
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
            teacher = TeacherUser.objects.get(full_name=teacher_name)
            return teacher.role  # Assuming 'role' is the field you want to retrieve
        except TeacherUser.DoesNotExist:
            return None

    def get_teacher(self, obj):
        schedule_data = obj.schedule_data
        if schedule_data:
            teacher_name = schedule_data[0]['teacher'] if schedule_data else None
            return teacher_name
        return None

    def get_role(self, obj):
        teacher_name = self.get_teacher(obj)
        return self.get_teacher_role(teacher_name) if teacher_name else None

    def get_total_classes(self, obj):
        schedule_data = obj.schedule_data
        return len(schedule_data) if schedule_data else 0

    def get_class_duration(self, obj):
        schedule_data = obj.schedule_data
        return schedule_data[0]['class_duration'] if schedule_data else 0


class ScheduleUpdateSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    schedule_data = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(max_length=100)  # Adjust max_length as needed
        ),
        allow_empty=True
    )

    class Meta:
        model = TeachersSchedule
        fields = ['start_date', 'end_date', 'schedule_data']

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
        instance.schedule_data = validated_data.get('schedule_data', instance.schedule_data)
        instance.save()  # Save the changes to the database
        return instance

