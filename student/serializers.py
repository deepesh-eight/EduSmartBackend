from rest_framework import serializers

from EduSmart import settings
from authentication.models import StudentUser, User
from authentication.serializers import AddressDetailsSerializer
from constants import USER_TYPE_CHOICES, GENDER_CHOICES, RELIGION_CHOICES, CLASS_CHOICES, BLOOD_GROUP_CHOICES
from curriculum.models import Curriculum


class StudentUserSignupSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=False, default='')
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )
    dob = serializers.DateField(required=True)
    image = serializers.ImageField(required=False, default='')
    father_name = serializers.CharField(required=False, default='')
    father_phone_number = serializers.CharField(required=False, default='')
    mother_name = serializers.CharField(required=False, default='')
    mother_occupation = serializers.CharField(required=False, default='')
    mother_phone_number = serializers.CharField(required=False, default='')
    gender = serializers.CharField(required=True)
    father_occupation = serializers.CharField(required=False, default='')
    admission_date = serializers.DateField(required=True)
    school_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    bus_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    canteen_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    other_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    due_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    religion = serializers.CharField(required=False, default='')
    blood_group = serializers.CharField(required=False, default='')
    class_enrolled = serializers.CharField(required=True)
    section = serializers.CharField(required=True)
    curriculum = serializers.CharField(required=True)
    permanent_address = serializers.CharField(max_length=255, required=False, default='')
    bus_number = serializers.CharField(required=False, default='')
    bus_route = serializers.IntegerField(required=False, default='')



class StudentDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    curriculum = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'image', 'class_enrolled', 'section', 'admission_date', 'dob', 'gender', 'religion', 'blood_group',
                  'school_fee','bus_fee', 'canteen_fee', 'other_fee', 'due_fee', 'total_fee', 'father_name', 'father_phone_number',
                  'father_occupation', 'mother_name', 'mother_phone_number', 'mother_occupation', 'email', 'permanent_address', 'curriculum',
                   'bus_number', 'bus_route']


    def get_curriculum(self,obj):
        return obj.curriculum.curriculum_name if hasattr(obj, 'curriculum') else None

    def get_image(self, obj):
        # Assuming 'image' field stores the file path or URL
        if obj.image:
            # Assuming media URL is configured in settings
            return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
        return None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None


class studentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=False)
    name = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )
    dob = serializers.DateField(required=True)
    image = serializers.ImageField(required=False)
    father_name = serializers.CharField(required=False)
    father_phone_number = serializers.CharField(required=False)
    mother_name = serializers.CharField(required=False)
    mother_occupation = serializers.CharField(required=False)
    mother_phone_number = serializers.CharField(required=False)
    gender = serializers.CharField(required=True)
    father_occupation = serializers.CharField(required=False)
    admission_date = serializers.DateField(required=True)
    school_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    bus_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    canteen_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    other_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    due_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    religion = serializers.CharField(required=False)
    blood_group = serializers.CharField(required=False)
    class_enrolled = serializers.CharField(required=True)
    section = serializers.CharField(required=True)
    curriculum = serializers.CharField(required=True)
    permanent_address = serializers.CharField(max_length=255, required=False)
    bus_number = serializers.CharField(required=False)
    bus_route = serializers.IntegerField(required=False)


    class Meta:
        model = StudentUser
        fields = ['name', 'email', 'user_type', 'dob', 'image', 'father_name', 'father_phone_number', 'father_occupation', 'mother_name',
                  'mother_occupation', 'mother_phone_number', 'gender', 'admission_date', 'school_fee', 'bus_fee', 'canteen_fee', 'other_fee',
                  'due_fee', 'total_fee', 'religion', 'blood_group', 'class_enrolled', 'section', 'curriculum', 'permanent_address', 'bus_number',
                  'bus_route']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        validated_data.pop('email', None)
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        curriculum_data = validated_data.pop('curriculum', None)
        if curriculum_data is not None:
            curriculum = Curriculum.objects.get(id=curriculum_data)
            instance.curriculum = curriculum
            instance.save()

        return super().update(instance, validated_data)

class StudentListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'class_enrolled', 'section', 'father_phone_number', 'permanent_address', 'image']

    def get_image(self, obj):
        # Assuming 'image' field stores the file path or URL
        if obj.image:
            # Assuming media URL is configured in settings
            return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
        return None