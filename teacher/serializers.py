from rest_framework import serializers

from authentication.models import TeacherUser
from constants import USER_TYPE_CHOICES, GENDER_CHOICES, RELIGION_CHOICES, BLOOD_GROUP_CHOICES, CLASS_CHOICES, \
    SUBJECT_CHOICES, ROLE_CHOICES


class TeacherUserSignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )
    dob = serializers.DateField(required=True)
    image = serializers.CharField(required=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True)
    joining_date = serializers.DateField(required=True)
    religion = serializers.ChoiceField(choices=RELIGION_CHOICES, required=True)
    blood_group = serializers.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False)
    ctc = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    class_taught = serializers.ListField(child=serializers.CharField(max_length=100))
    section = serializers.CharField(max_length=100, required=True)
    subject = serializers.ListField(child=serializers.CharField(max_length=100))
    experience = serializers.IntegerField(required=False)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=True)
    address = serializers.CharField(max_length=255, required=False)


class TeacherDetailSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    class_taught = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()

    class Meta:
        model = TeacherUser
        fields = ['id', 'full_name', 'gender', 'dob', 'blood_group', 'phone', 'address', 'email', 'religion',
                  'role', 'joining_date', 'class_taught', 'experience', 'subject', 'section', 'ctc']

    def get_name(self, obj):
        return obj.user.name if hasattr(obj, 'user') else None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

    def get_subject(self, obj):
        subjects_str = obj.subject
        if subjects_str:
            return eval(subjects_str)
        return []

    def get_class_taught(self, obj):
        subjects_str = obj.class_taught
        if subjects_str:
            return eval(subjects_str)
        return []


class TeacherListSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    phone = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    class_taught = serializers.SerializerMethodField()

    class Meta:
        model = TeacherUser
        fields = ['id', 'full_name', 'subject', 'class_taught', 'phone', 'email']

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

    def get_subject(self, obj):
        subjects_str = obj.subject
        if subjects_str:
            return eval(subjects_str)
        return []

    def get_class_taught(self, obj):
        subjects_str = obj.class_taught
        if subjects_str:
            return eval(subjects_str)
        return []


class TeacherProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    phone = serializers.CharField(source='user.phone')
    full_name = serializers.CharField(required=False)
    dob = serializers.DateField(required=True)
    image = serializers.CharField(required=True)
    gender = serializers.ChoiceField(choices=GENDER_CHOICES, required=True)
    joining_date = serializers.DateField(required=True)
    religion = serializers.ChoiceField(choices=RELIGION_CHOICES, required=True)
    blood_group = serializers.ChoiceField(choices=BLOOD_GROUP_CHOICES, required=False)
    ctc = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    class_taught = serializers.ListField(child=serializers.CharField(max_length=100))
    section = serializers.CharField(max_length=100, required=True)
    subject = serializers.ListField(child=serializers.CharField(max_length=100))
    experience = serializers.IntegerField(required=False)
    role = serializers.ChoiceField(choices=ROLE_CHOICES, required=True)
    address = serializers.CharField(max_length=255, required=False)


    class Meta:
        model = TeacherUser
        fields = ['full_name', 'email', 'phone', 'dob', 'image', 'joining_date', 'religion', 'subject', 'experience', 'role', 'address',
                  'ctc', 'blood_group', 'class_taught', 'section', 'address', 'gender']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        return super().update(instance, validated_data)
