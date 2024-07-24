import pytz
from django.contrib.auth.hashers import make_password
from django.core.validators import RegexValidator
from rest_framework import serializers

from EduSmart import settings
from authentication.models import User, InquiryForm
from constants import USER_TYPE_CHOICES
from student.serializers import ImageFieldStringAndFile
from superadmin.models import SchoolProfile, SchoolProfilePassword, CurricullumList, Subjects


class SchoolCreateSerializer(serializers.Serializer):
    logo = serializers.ImageField(required=False, default='')
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )
    school_name = serializers.CharField(max_length=255, default='')
    address = serializers.CharField(max_length=255, default='')
    city = serializers.CharField(max_length=255, default='')
    state = serializers.CharField(max_length=255, default='')
    established_year = serializers.IntegerField(default='')
    school_type = serializers.CharField(max_length=255, default='')
    principle_name = serializers.CharField(max_length=255, default='')
    contact_no = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Contact number must be exactly 10 digits."
            )
        ]
    )
    email = serializers.CharField(max_length=255, default='')
    school_website = serializers.URLField(default='')
    school_id = serializers.CharField(max_length=255, default='')
    contract = serializers.FileField(required=False)
    description = serializers.CharField(max_length=255, default='')


class SchoolProfileSerializer(serializers.ModelSerializer):
    # logo = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    principle_name = serializers.SerializerMethodField()
    # contract = serializers.SerializerMethodField()
    class Meta:
        model = SchoolProfile
        fields = ['id', 'school_id', 'logo', 'school_name', 'address', 'city', 'state', 'established_year', 'school_type',
                  'principle_name', 'contact_no', 'email', 'school_website', 'description', 'contract']

    # def get_logo(self, obj):
    #     if obj.logo:
    #         if obj.logo.name.startswith(settings.base_url + settings.MEDIA_URL):
    #             return str(obj.logo)
    #         else:
    #             return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.logo)}'
    #     return None

    def get_principle_name(self, obj):
        return obj.user.name

    def get_email(self, obj):
        return obj.user.email

    # def get_contract(self, obj):
    #     if obj.contract:
    #         if obj.contract.name.startswith(settings.base_url + settings.MEDIA_URL):
    #             return str(obj.contract)
    #         else:
    #             return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.contract)}'
    #     return None


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'school_id']


class SchoolProfileUpdateSerializer(serializers.ModelSerializer):
    contact_no = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Contact number must be exactly 10 digits."
            )
        ]
    )
    email = serializers.CharField(write_only=True)
    school_id = serializers.CharField(max_length=255)
    principle_name = serializers.CharField(max_length=255)
    contract = ImageFieldStringAndFile(required=False)
    class Meta:
        model = SchoolProfile
        fields = ['logo', 'school_name', 'address', 'city', 'state', 'established_year', 'school_type',
                  'principle_name', 'contact_no', 'email', 'school_website', 'school_id', 'contract', 'description']

    def update(self, instance, validated_data):
        # Extract data for User model
        user_data = {
            'email': validated_data.pop('email', None),
            'name': validated_data.pop('principle_name', None),
        }

        # Update User model
        user = instance.user
        for attr, value in user_data.items():
            if value is not None:  # Only update if value is provided
                setattr(user, attr, value)
        user.save()

        # Update SchoolProfile model
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance


class SubjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['primary_subject', 'optional_subject']


class CurriculumCreateSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(required=True)
    class_name = serializers.CharField(required=True)
    primary_subject = serializers.ListField(child=serializers.CharField(), required=False)
    optional_subject = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = CurricullumList
        fields = ['id', 'curriculum_name', 'class_name', 'primary_subject', 'optional_subject']

    def create(self, validated_data):
        primary_subjects_data = validated_data.pop('primary_subject', [])
        optional_subjects_data = validated_data.pop('optional_subject', [])

        curriculum = CurricullumList.objects.create(**validated_data)

        max_index = max(len(primary_subjects_data), len(optional_subjects_data))

        for index in range(max_index):
            primary_subject = primary_subjects_data[index] if index < len(primary_subjects_data) else None
            optional_subject = optional_subjects_data[index] if index < len(optional_subjects_data) else None

            Subjects.objects.create(
                curriculum_id=curriculum,
                primary_subject=primary_subject.strip() if primary_subject else None,
                optional_subject=optional_subject.strip() if optional_subject else None
            )

        return curriculum

    def validate(self, data):
        curriculum_name = data.get('curriculum_name')
        class_name = data.get('class_name')

        data['curriculum_name'] = data['curriculum_name'].upper()
        data['class_name'] = data['class_name'].upper()
        if CurricullumList.objects.filter(curriculum_name=data['curriculum_name'], class_name=data['class_name']).exists():
            raise serializers.ValidationError(
                f"A curriculum with name {curriculum_name} and class {class_name} already exists.")

        return data


class CurriculumUpdateSerializer(serializers.ModelSerializer):
    # subjects = SubjectsSerializer(required=False, many=True)
    class Meta:
        model = CurricullumList
        fields = ['curriculum_name', 'class_name',]

    # def validate_class_subject(self, value):
    #     updated_subjects = self.process_subjects(value)
    #     return updated_subjects

    def update(self, instance, validated_data):
        instance.curriculum_name = validated_data.get('curriculum_name', instance.curriculum_name)
        instance.class_name = validated_data.get('class_name', instance.class_name)
        instance.save()

        request = self.context.get('request')
        if not request:
            raise ValueError("Request is not in context")

        primary_subjects = []
        optional_subjects = []

        for key in request.data.keys():
            if key.startswith('primary_subject'):
                primary_subjects.append(request.data[key])
            if key.startswith('optional_subject'):
                optional_subjects.append(request.data[key])

        if not primary_subjects or not optional_subjects:
            raise ValueError("Primary or Optional subjects are missing")

        Subjects.objects.filter(curriculum_id=instance.id).delete()

        for primary_subject, optional_subject in zip(primary_subjects, optional_subjects):
            Subjects.objects.create(
                curriculum_id=instance,
                primary_subject=primary_subject.strip() if primary_subject else None,
                optional_subject=optional_subject.strip() if optional_subject else None
            )

        return instance

    def validate(self, data):
        curriculum_name = data.get('curriculum_name')
        class_name = data.get('class_name')

        data['curriculum_name'] = data['curriculum_name'].upper()
        data['class_name'] = data['class_name'].upper()

        if CurricullumList.objects.filter(curriculum_name=data['curriculum_name'],
                                     class_name=data['class_name']).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(
                f"A curriculum with name {curriculum_name} and class {class_name} already exists.")

        return data


class CurriculumListSerializer(serializers.ModelSerializer):
    primary_subject = serializers.SerializerMethodField()
    optional_subject = serializers.SerializerMethodField()
    class Meta:
        model = CurricullumList
        fields = ['id', 'curriculum_name', 'class_name', 'primary_subject', 'optional_subject']

    def get_primary_subject(self, obj):
        primary_subject = Subjects.objects.filter(curriculum_id=obj.id)
        subjcet_list = []
        if primary_subject:
            for subject_list in primary_subject:
                subject = subject_list.primary_subject
                subjcet_list.append(subject)
            return subjcet_list
        else:
            None

    def get_optional_subject(self, obj):
        optional_subject = Subjects.objects.filter(curriculum_id=obj.id)
        subjcet_list = []
        if optional_subject:
            for subject_list in optional_subject:
                subject = subject_list.optional_subject
                subjcet_list.append(subject)
            return subjcet_list
        else:
            None


class SuperAdminCurriculumSubjectList(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['primary_subject']


class SuperAdminCurriculumOptionalSubjectList(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['optional_subject']


class SuperAdminProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'user_type', 'name', 'email']


class InquiryListSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    time = serializers.SerializerMethodField()

    class Meta:
        model = InquiryForm
        fields = ['id', 'name', 'phone_number', 'e_mail', 'description', 'date', 'time']

    def get_date(self, obj):
        return obj.updated_at.date()

    def get_time(self, obj):
        utc_time = obj.updated_at.replace(tzinfo=pytz.utc)  # Make sure to set timezone info to UTC
        ist_timezone = pytz.timezone('Asia/Kolkata')
        ist_time = utc_time.astimezone(ist_timezone)

        # Format time in AM/PM format
        ist_time_am_pm = ist_time.strftime("%I:%M %p")

        return ist_time_am_pm