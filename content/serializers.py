import json
from rest_framework import serializers
from .models import Content, Curriculum

class CurriculumData(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['curriculum_name']

class ContentSerializer(serializers.ModelSerializer):
    curriculum = serializers.SerializerMethodField()
    class Meta:
        model = Content
        fields = ['id','curriculum','content_media','content_media_link','content_type','content_name','content_creator','supporting_detail','description','is_recommended','classes','subject']

    def get_curriculum(self, obj):
        return obj.curriculum.curriculum_name if obj.curriculum else None