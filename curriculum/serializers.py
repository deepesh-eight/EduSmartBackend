import json

from rest_framework import serializers

from EduSmart import settings
from curriculum.models import Curriculum, CurriculumPDF
from student.serializers import ImageFieldStringAndFile
from superadmin.models import CurricullumList


class CurriculumSerializer(serializers.ModelSerializer):
    academic_session = serializers.CharField(max_length=255, required=False)
    exam_board = serializers.CharField(max_length=255, required=False)
    subject_name_code = serializers.CharField(max_length=255, required=False)
    class_name = serializers.CharField(max_length=255, required=False)
    section = serializers.CharField(max_length=255, required=False)
    curriculum_name = serializers.CharField(max_length=255, required=False)

    class Meta:
        model = Curriculum
        fields = ['academic_session', 'exam_board', 'subject_name_code', 'class_name', 'section', 'curriculum_name']


class CurriculumSerializer(serializers.ModelSerializer):

    class Meta:
        model = Curriculum
        fields = ['id', 'academic_session', 'curriculum_name', 'select_class', 'primary_subject', 'optional_subject', 'syllabus', 'discription']

    def validate_primary_subject(self, value):
        updated_subjects = []
        for subject in value:
            # Convert the first character to uppercase
            subject = subject.capitalize()
            # Convert characters after space to uppercase
            subject = ' '.join(word.capitalize() for word in subject.split(' '))
            updated_subjects.append(subject)
        return updated_subjects

    def validate_optional_subject(self, value):
        updated_subjects = []
        for subject in value:
            # Convert the first character to uppercase
            subject = subject.capitalize()
            # Convert characters after space to uppercase
            subject = ' '.join(word.capitalize() for word in subject.split(' '))
            updated_subjects.append(subject)
        return updated_subjects

    def validate(self, data):
        curriculum_name = data.get('curriculum_name')
        class_name = data.get('select_class')

        # Check if a curriculum with the provided name and class already exists
        if Curriculum.objects.filter(curriculum_name=curriculum_name, select_class=class_name).exists():
            raise serializers.ValidationError(f"A curriculum with name {curriculum_name} and class {class_name} already exists.")

        return data



class CurriculumListerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['id', 'academic_session', 'curriculum_name', 'select_class', 'discription']


class CurriculumUploadSerializer(serializers.Serializer):
    academic_session = serializers.CharField(required=False)
    exam_board = serializers.CharField(required=False)
    class_name = serializers.CharField(required=False)
    section = serializers.CharField(required=False)
    subject_name_code = serializers.CharField()
    curriculum_pdf_file = serializers.FileField(required=False)

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        try:
            subject_name_code_str = json.loads(
                data.get('subject_name_code', '[]'))  # Parse string input as JSON
            ret['subject_name_code'] = subject_name_code_str
        except json.JSONDecodeError:
            raise serializers.ValidationError({'subject_name_code': 'Invalid JSON format'})

        return ret


class CurriculumDetailSerializer(serializers.ModelSerializer):
    syllabus = serializers.SerializerMethodField()
    class Meta:
        model = Curriculum
        fields = ['id', 'curriculum_name', 'select_class', 'academic_session', 'primary_subject', 'optional_subject', 'syllabus', 'discription']

    def get_syllabus(self, obj):
        if obj.syllabus:
            if obj.syllabus.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.syllabus)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.syllabus)}'
        return None


class CurriculumDetailUpdateSerializer(serializers.ModelSerializer):
    syllabus = ImageFieldStringAndFile(required=False)
    class Meta:
        model = Curriculum
        fields = ['id', 'curriculum_name', 'select_class', 'academic_session', 'primary_subject', 'optional_subject', 'syllabus', 'discription']


    def validate_primary_subject(self, value):
        updated_subjects = []
        for subject in value:
            # Convert the first character to uppercase
            subject = subject.capitalize()
            # Convert characters after space to uppercase
            subject = ' '.join(word.capitalize() for word in subject.split(' '))
            updated_subjects.append(subject)
        return updated_subjects

    def validate_optional_subject(self, value):
        updated_subjects = []
        for subject in value:
            # Convert the first character to uppercase
            subject = subject.capitalize()
            # Convert characters after space to uppercase
            subject = ' '.join(word.capitalize() for word in subject.split(' '))
            updated_subjects.append(subject)
        return updated_subjects

class SuperAdminCurriculumClassList(serializers.ModelSerializer):
    class Meta:
        model = CurricullumList
        fields = ['class_name']


class SuperAdminCurriculumSubjectList(serializers.ModelSerializer):
    class Meta:
        model = CurricullumList
        fields = ['class_subject']


class SuperAdminCurriculumOptionalSubjectList(serializers.ModelSerializer):
    class Meta:
        model = CurricullumList
        fields = ['optional_subject']