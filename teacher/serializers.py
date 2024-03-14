from rest_framework import serializers

from authentication.models import TeacherUser, StudentUser
from authentication.serializers import AddressDetailsSerializer
from constants import USER_TYPE_CHOICES, GENDER_CHOICES, RELIGION_CHOICES, BLOOD_GROUP_CHOICES, CLASS_CHOICES


class TeacherUserSignupSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )

    # address details
    address_line_1 = serializers.CharField(required=True)
    address_line_2 = serializers.CharField(required=False)
    city = serializers.CharField(required=True)
    state = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    pincode = serializers.CharField(required=True)

    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    dob = serializers.DateField(required=True)
    image = serializers.ImageField(required=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True)
    joining_date = serializers.DateField(required=True)
    religion = serializers.ChoiceField(choices=RELIGION_CHOICES, required=True)
    blood_group = serializers.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False)
    salary = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)

    class_name = serializers.MultipleChoiceField(choices=CLASS_CHOICES, required=True)
    section = serializers.CharField(max_length=100, required=True)


class TeacherDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = TeacherUser
        fields = ['id', 'name', 'gender', 'dob', 'religion', 'email',
                  'salary', 'joining_date']

    def get_name(self, obj):
        return obj.user.name if hasattr(obj, 'user') else None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None


class TeacherListSerializer(serializers.ModelSerializer):
    address_detail = AddressDetailsSerializer(source='user.address_details', many=True)
    name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'gender', 'phone', 'dob', 'address_detail']

    def get_name(self, obj):
        return obj.user.name if hasattr(obj, 'user') else None

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None


class TeacherProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    class_name = serializers.CharField(required=False)
    section = serializers.CharField(required=False)

    class Meta:
        model = TeacherUser
        fields = ['name', 'email', 'phone', 'dob', 'image', 'first_name', 'last_name', 'salary',
                  'blood_group', 'class_name', 'section']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        return super().update(instance, validated_data)
