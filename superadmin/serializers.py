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