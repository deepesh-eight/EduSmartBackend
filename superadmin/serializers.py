from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from EduSmart import settings
from authentication.models import User
from constants import USER_TYPE_CHOICES
from student.serializers import ImageFieldStringAndFile
from superadmin.models import SchoolProfile, SchoolProfilePassword


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


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'school_id']


class SchoolProfileUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    logo = ImageFieldStringAndFile(required=False)

    class Meta:
        model = SchoolProfile
        fields = ['logo', 'school_name', 'address', 'city', 'state', 'established_year', 'school_type',
                  'principle_name', 'contact_no', 'email', 'school_website', 'school_id', 'password', 'description']

    def validate(self, data):
        # Custom validation logic if needed (e.g., unique school ID)
        return data

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        school_profile_data = validated_data

        # Update User data (name, email, password)
        user_serializer = UserUpdateSerializer(instance.user, data=user_data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()

        # Update SchoolProfile data (school_id, principle_name, ...)
        for field, value in school_profile_data.items():
            setattr(instance, field, value)
        instance.save()

        return instance