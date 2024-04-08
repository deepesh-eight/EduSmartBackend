import json

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from EduSmart import settings
from authentication.models import TeacherUser, Certificate
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
        # Assuming 'image' field stores the file path or URL
        if obj.image:
            # Assuming media URL is configured in settings
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
