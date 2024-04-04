from rest_framework import serializers

from curriculum.models import Curriculum


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
        fields = ['id', 'academic_session', 'exam_board', 'subject_name_code', 'class_name', 'section', 'curriculum_name']