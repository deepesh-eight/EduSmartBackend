import json

from rest_framework import serializers

from superadmin.models import CurricullumList
from EduSmart import settings
from curriculum.models import Curriculum, Subjects
from student.serializers import ImageFieldStringAndFile



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


class CurriculumSubjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['primary_subject', 'optional_subject']


class CurriculumSerializer(serializers.ModelSerializer):
    curriculum_name = serializers.CharField(required=True)
    # class_name = serializers.CharField(required=True)
    primary_subject = serializers.ListField(child=serializers.CharField(), required=False)
    optional_subject = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Curriculum
        fields = ['id', 'curriculum_name', 'select_class', 'primary_subject', 'optional_subject', 'syllabus', 'discription', 'curriculum_type']

    def create(self, validated_data):
        primary_subjects_data = validated_data.pop('primary_subject', [])
        optional_subjects_data = validated_data.pop('optional_subject', [])

        curriculum = Curriculum.objects.create(**validated_data)

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
        class_name = data.get('select_class')

        data['curriculum_name'] = data['curriculum_name'].upper()
        data['select_class'] = data['select_class'].upper()
        if Curriculum.objects.filter(curriculum_name=data['curriculum_name'], select_class=data['select_class']).exists():
            raise serializers.ValidationError(
                f"A curriculum with name {curriculum_name} and class {class_name} already exists.")

        return data



class CurriculumListerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['id', 'curriculum_name', 'select_class', 'discription']


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
    primary_subject = serializers.SerializerMethodField()
    optional_subject = serializers.SerializerMethodField()

    class Meta:
        model = Curriculum
        fields = ['id', 'curriculum_name', 'select_class', 'primary_subject', 'optional_subject', 'syllabus', 'discription', 'curriculum_type']

    def get_syllabus(self, obj):
        if obj.syllabus:
            if obj.syllabus.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.syllabus)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.syllabus)}'
        return None

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


class CurriculumDetailUpdateSerializer(serializers.ModelSerializer):
    syllabus = ImageFieldStringAndFile(required=False)
    # subjects = CurriculumSubjectsSerializer(many=True, required=False)
    class Meta:
        model = Curriculum
        fields = ['id', 'curriculum_name', 'select_class', 'syllabus', 'discription']

    def update(self, instance, validated_data):
        instance.curriculum_name = validated_data.get('curriculum_name', instance.curriculum_name)
        instance.select_class = validated_data.get('select_class', instance.select_class)
        instance.discription = validated_data.get('discription', instance.discription)
        instance.syllabus = validated_data.get('syllabus', instance.syllabus)
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
        class_name = data.get('select_class')

        data['curriculum_name'] = data['curriculum_name'].upper()
        data['select_class'] = data['select_class'].upper()

        if Curriculum.objects.filter(curriculum_name=data['curriculum_name'], select_class=data['select_class']).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError(
                f"A curriculum with name {curriculum_name} and class {class_name} already exists.")

        return data

class SuperAdminCurriculumClassList(serializers.ModelSerializer):
    class Meta:
        model = CurricullumList
        fields = ['class_name']


