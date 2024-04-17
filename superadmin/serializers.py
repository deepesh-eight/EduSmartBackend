from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from EduSmart import settings
from superadmin.models import SchoolProfile, SchoolProfilePassword


class SchoolCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = SchoolProfile
        fields = ['logo', 'school_name', 'address', 'city', 'state', 'established_year', 'school_type',
                  'principle_name', 'contact_no', 'email', 'school_website', 'school_id', 'password', 'description']

    def create(self, validated_data):
        password = validated_data.pop('password')

        if len(password) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long')
        validated_data['password'] = make_password(password)
        school_profile = super().create(validated_data)
        return school_profile


class SchoolProfileSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    password = serializers.CharField()
    class Meta:
        model = SchoolProfile
        fields = ['id', 'school_id', 'logo', 'school_name', 'address', 'city', 'state', 'established_year', 'school_type',
                  'principle_name', 'contact_no', 'email', 'school_website', 'description', 'password']

    def get_logo(self, obj):
        if obj.logo:
            if obj.logo.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.logo)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.logo)}'
        return None
