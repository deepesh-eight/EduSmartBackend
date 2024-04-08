import json

from rest_framework import serializers

from curriculum.models import Curriculum, CurriculumPDF


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
    subject_name_code = serializers.CharField()

    class Meta:
        model = Curriculum
        fields = ['id', 'academic_session', 'exam_board', 'subject_name_code', 'class_name', 'section', 'curriculum_name']

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        try:
            subject_name_code_str = json.loads(
                data.get('subject_name_code', '[]'))  # Parse string input as JSON
            ret['subject_name_code'] = subject_name_code_str
        except json.JSONDecodeError:
            raise serializers.ValidationError({'subject_name_code': 'Invalid JSON format'})

        return ret

class CurriculumListerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['id', 'academic_session', 'exam_board', 'subject_name_code', 'class_name', 'section', 'curriculum_name']


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
    class Meta:
        model = Curriculum
        fields = ['curriculum_name',]
