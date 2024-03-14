from rest_framework import serializers

from authentication.models import StudentUser
from authentication.serializers import AddressDetailsSerializer
from constants import USER_TYPE_CHOICES, GENDER_CHOICES, RELIGION_CHOICES, CLASS_CHOICES, BLOOD_GROUP_CHOICES


class StudentUserSignupSerializer(serializers.Serializer):
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

    dob = serializers.DateField(required=True)
    image = serializers.ImageField(required=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True)
    father_name = serializers.CharField(required=True)
    mother_name = serializers.CharField(required=True)
    father_occupation = serializers.CharField(required=True)
    admission_date = serializers.DateField(required=True)
    religion = serializers.ChoiceField(choices=RELIGION_CHOICES, required=True)
    school_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    bus_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    canteen_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    other_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_amount = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    blood_group = serializers.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False)

    class_name = serializers.ChoiceField(choices=CLASS_CHOICES, required=True)
    section = serializers.CharField(max_length=100, required=True)


class StudentDetailSerializer(serializers.ModelSerializer):
    # address_detail = AddressDetailsSerializer(source='user.address_details', many=True)
    name = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'gender', 'father_name', 'mother_name', 'dob', 'religion', 'father_occupation', 'email',
                  'admission_date']

    def get_name(self, obj):
        return obj.user.name if hasattr(obj, 'user') else None

    # def get_phone(self, obj):
    #     phone_number = obj.user.phone
    #     if phone_number:
    #         return str(phone_number)
    #     return None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None


class studentProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    class_name = serializers.CharField(source='class_enrolled.class_name')
    section = serializers.CharField(source='class_enrolled.section')


    class Meta:
        model = StudentUser
        fields = ['name', 'email', 'phone', 'dob', 'image', 'father_name', 'mother_name', 'school_fee', 'bus_fee',
                  'canteen_fee', 'other_fee', 'total_amount', 'blood_group', 'class_name', 'section']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        class_data = validated_data.pop('class_enrolled', {})
        class_info = instance.class_enrolled

        for attr, value in class_data.items():
            setattr(class_info, attr, value)
        class_info.save()

        return super().update(instance, validated_data)

class StudentListSerializer(serializers.ModelSerializer):
    address_detail = AddressDetailsSerializer(source='user.address_details', many=True)
    name = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'gender', 'father_name', 'dob', 'address_detail']

    def get_name(self, obj):
        return obj.user.name if hasattr(obj, 'user') else None

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None