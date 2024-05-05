from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from EduSmart import settings
from authentication.models import User
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
    contact_no = serializers.CharField(max_length=255, default='')
    email = serializers.CharField(max_length=255, default='')
    school_website = serializers.URLField(default='')
    school_id = serializers.CharField(max_length=255, default='')
    password = serializers.CharField(max_length=255, default='')
    description = serializers.CharField(max_length=255, default='')


class SchoolProfileSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    principle_name = serializers.SerializerMethodField()
    password = serializers.CharField()
    decrypted_password = serializers.CharField(read_only=True, source='get_decrypted_password')
    class Meta:
        model = SchoolProfile
        fields = ['id', 'school_id', 'logo', 'school_name', 'address', 'city', 'state', 'established_year', 'school_type',
                  'principle_name', 'contact_no', 'email', 'school_website', 'description', 'password', 'decrypted_password']

    def get_logo(self, obj):
        if obj.logo:
            if obj.logo.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.logo)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.logo)}'
        return None

    def get_principle_name(self, obj):
        return obj.user.name

    def get_email(self, obj):
        return obj.user.email

class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'school_id']


class SchoolProfileUpdateSerializer(serializers.ModelSerializer):
    email = serializers.CharField(write_only=True)
    school_id = serializers.CharField(write_only=True)
    principle_name = serializers.CharField(max_length=255)
    class Meta:
        model = SchoolProfile
        fields = ['logo', 'school_name', 'address', 'city', 'state', 'established_year', 'school_type',
                  'principle_name', 'contact_no', 'email', 'school_website', 'school_id', 'password', 'description']

    def update(self, instance, validated_data):
        # Extract data for User model
        user_data = {
            'email': validated_data.pop('email', None),
            'school_id': validated_data.pop('school_id', None),
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
    subjects = SubjectsSerializer(many=True, required=False)

    class Meta:
        model = CurricullumList
        fields = ['curriculum_name', 'class_name', 'subjects']

    def create(self, validated_data):
        subjects_data = validated_data.pop('subjects')
        curriculum = CurricullumList.objects.create(**validated_data)

        for subject_data in subjects_data:
            Subjects.objects.create(curriculum_id=curriculum, **subject_data)

        return curriculum

    def validate(self, data):
        curriculum_name = data.get('curriculum_name')
        class_name = data.get('class_name')

        # Check if a curriculum with the provided name and class already exists
        if CurricullumList.objects.filter(curriculum_name=curriculum_name, class_name=class_name).exists():
            raise serializers.ValidationError(f"A curriculum with name {curriculum_name} and class {class_name} already exists.")

        return data


class CurriculumUpdateSerializer(serializers.ModelSerializer):
    subjects = SubjectsSerializer(required=False, many=True)
    class Meta:
        model = CurricullumList
        fields = ['curriculum_name', 'class_name', 'subjects',]

    def validate_class_subject(self, value):
        updated_subjects = self.process_subjects(value)
        return updated_subjects

    def update(self, instance, validated_data):
        instance.curriculum_name = validated_data.get('curriculum_name', instance.curriculum_name)
        instance.class_name = validated_data.get('class_name', instance.class_name)
        instance.save()

        # Handle update logic for associated subjects
        subjects_data = validated_data.pop('subjects', [])
        existing_subjects = Subjects.objects.filter(curriculum_id=instance.id)

        for subject_data, subject_instance in zip(subjects_data, existing_subjects):
            subject_instance.primary_subject = subject_data.get('primary_subject', subject_instance.primary_subject)
            subject_instance.optional_subject = subject_data.get('optional_subject', subject_instance.optional_subject)
            subject_instance.save()

        return instance
    # def validate_class_subject(self, value):
    #     updated_subjects = self.process_subjects(value)
    #     return updated_subjects
    #
    # def validate_optional_subject(self, value):
    #     updated_subjects = self.process_subjects(value)
    #     return updated_subjects
    #
    # def process_subjects(self, subjects):
    #     updated_subjects = []
    #     for subject in subjects:
    #         # Format subject code
    #         subject_code = self.generate_subject_code(subject)
    #         # Format subject name
    #         formatted_subject = self.format_subject_name(subject)
    #         updated_subjects.append(subject_code)
    #     return updated_subjects
    #
    # def generate_subject_code(self, subject_code):
    #     parts = subject_code.split('-')
    #     if len(parts) == 2:
    #         code = parts[0]
    #         subject_name = parts[1]
    #         if code.isdigit() and len(code) < 3:
    #             code = code.zfill(3)  # Pad with leading zeros if necessary
    #             return f"{code}-{self.format_subject_name(subject_name)}"
    #     return subject_code
    #
    # def format_subject_name(self, subject_name):
    #     # Capitalize first letter of each word in subject name
    #     return ' '.join(word.capitalize() for word in subject_name.split())


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