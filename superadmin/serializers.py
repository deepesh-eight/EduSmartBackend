from rest_framework import serializers

from superadmin.models import SchoolProfile


class SchoolCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = SchoolProfile
        fields = ['logo', 'school_name', 'address', 'city', 'state', 'established_year', 'school_type', 'principle_name', 'contact_no', 'email', 'school_website', 'description']