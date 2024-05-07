import json
from rest_framework import serializers

from EduSmart import settings
from .models import Content, Curriculum

class CurriculumData(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['curriculum_name']

class ContentSerializer(serializers.ModelSerializer):
    # curriculum = serializers.SerializerMethodField()
    class Meta:
        model = Content
        fields = ['id','curriculum','content_media','content_media_link','image', 'content_type','content_name','content_creator','supporting_detail','description','is_recommended','classes','subject']

    # def get_curriculum(self, obj):
    #     return obj.curriculum.curriculum_name if obj.curriculum else None


class ContentListSerializer(serializers.ModelSerializer):
    # curriculum = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    content_media = serializers.SerializerMethodField()
    class Meta:
        model = Content
        fields = ['id','curriculum','content_media', 'image', 'content_media_link','content_type','content_name','content_creator','supporting_detail','description','is_recommended','classes','subject']

    # def get_curriculum(self, obj):
    #     return obj.curriculum.curriculum_name if obj.curriculum else None

    def get_image(self, obj):
        if obj.image:
            if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
        return None

    def get_content_media(self, obj):
        if obj.content_media:
            if obj.content_media.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.content_media)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.content_media)}'
        return None