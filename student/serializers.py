import datetime

from rest_framework import serializers

from EduSmart import settings
from authentication.models import StudentUser, User
from authentication.serializers import AddressDetailsSerializer
from constants import USER_TYPE_CHOICES, GENDER_CHOICES, RELIGION_CHOICES, CLASS_CHOICES, BLOOD_GROUP_CHOICES, \
    ATTENDENCE_CHOICE
from curriculum.models import Curriculum, Subjects
from student.models import StudentAttendence


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
    religion = serializers.CharField(required=True)
    blood_group = serializers.CharField(required=False, default='')
    class_enrolled = serializers.CharField(required=True)
    section = serializers.CharField(required=True)
    curriculum = serializers.CharField(required=True)
    permanent_address = serializers.CharField(max_length=255, required=False, default='')
    bus_number = serializers.CharField(required=False, default='')
    bus_route = serializers.IntegerField(required=False, default='')
    enrollment_no = serializers.CharField(default='')
    roll_no = serializers.CharField(default='')
    guardian_no = serializers.CharField(default='')
    optional_subject = serializers.CharField(default='')


class StudentDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    curriculum = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()
    # optional_subjects = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'image', 'class_enrolled', 'section', 'admission_date', 'dob', 'gender', 'religion', 'blood_group',
                  'school_fee','bus_fee', 'canteen_fee', 'other_fee', 'due_fee', 'total_fee', 'father_name', 'father_phone_number',
                  'father_occupation', 'mother_name', 'mother_phone_number', 'mother_occupation', 'email', 'permanent_address', 'curriculum',
                   'subjects', 'bus_number', 'bus_route', 'enrollment_no', 'roll_no', 'optional_subject', 'guardian_no']


    def get_curriculum(self,obj):
        return obj.curriculum if hasattr(obj, 'curriculum') else None

    def get_image(self, obj):
        if obj.image:
            if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
        return None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None

    def get_subjects(self, obj):
        try:
            curriculum = Curriculum.objects.get(curriculum_name=obj.curriculum, select_class=obj.class_enrolled)
            subject_data = Subjects.objects.filter(curriculum_id=curriculum.id)
            subjects = []
            for subject in subject_data:
                subjects.append(subject.primary_subject)
            return subjects or None
        except Curriculum.DoesNotExist as e:
            raise serializers.ValidationError(f"Error retrieving subjects: {str(e)}")

    # def get_optional_subjects(self, obj):
    #     try:
    #         curriculum = Curriculum.objects.get(curriculum_name=obj.curriculum, select_class=obj.class_enrolled)
    #         subject_data = Subjects.objects.filter(curriculum_id=curriculum.id)
    #         subject = []
    #         for subject_list in subject_data:
    #             subject.append(subject_list.optional_subject)
    #         return subject or None
    #
    #     except Curriculum.DoesNotExist as e:
    #         raise serializers.ValidationError(f"Error retrieving subjects: {str(e)}")


class ImageFieldStringAndFile(serializers.Field):
    def to_representation(self, value):
        if value:
            # Assuming value is a file path string
            return value.url if hasattr(value, 'url') else value
        return None

    def to_internal_value(self, data):
        # If data is a file object, return it as is
        if hasattr(data, 'content_type'):
            return data
        # If data is a string (file path), return it as is
        elif isinstance(data, str):
            return data
        else:
            raise serializers.ValidationError('Invalid file type. Must be a file object or a string representing a file path.')

class studentProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', required=False)
    name = serializers.CharField(required=False)
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )
    dob = serializers.DateField(required=False)
    image = ImageFieldStringAndFile(required=False)
    father_name = serializers.CharField(required=False)
    father_phone_number = serializers.CharField(required=False)
    mother_name = serializers.CharField(required=False)
    mother_occupation = serializers.CharField(required=False)
    mother_phone_number = serializers.CharField(required=False)
    gender = serializers.CharField(required=True)
    father_occupation = serializers.CharField(required=False)
    admission_date = serializers.DateField(required=False)
    school_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    bus_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    canteen_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    other_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    due_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    total_fee = serializers.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    religion = serializers.CharField(required=False)
    blood_group = serializers.CharField(required=False)
    class_enrolled = serializers.CharField(required=False)
    section = serializers.CharField(required=False)
    curriculum = serializers.CharField(required=False)
    permanent_address = serializers.CharField(max_length=255, required=False)
    bus_number = serializers.CharField(required=False)
    bus_route = serializers.IntegerField(required=False)
    guardian_no = serializers.CharField(default='')
    optional_subject = serializers.CharField(default='')


    class Meta:
        model = StudentUser
        fields = ['name', 'email', 'user_type', 'dob', 'image', 'father_name', 'father_phone_number', 'father_occupation', 'mother_name',
                  'mother_occupation', 'mother_phone_number', 'gender', 'admission_date', 'school_fee', 'bus_fee', 'canteen_fee', 'other_fee',
                  'due_fee', 'total_fee', 'religion', 'blood_group', 'class_enrolled', 'section', 'curriculum', 'permanent_address', 'bus_number',
                  'bus_route', 'guardian_no', 'optional_subject']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        validated_data.pop('email', None)
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # curriculum_data = validated_data.pop('curriculum', None)
        # if curriculum_data is not None:
        #     curriculum = Curriculum.objects.get(id=curriculum_data)
        #     instance.curriculum = curriculum
        #     instance.save()

        return super().update(instance, validated_data)

class StudentListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'class_enrolled', 'section', 'father_phone_number', 'image', 'email']

    def get_image(self, obj):
        if obj.image:
            if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
        return None

    def get_email(self, obj):
        return obj.user.email


class StudentAttendanceDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = StudentAttendence
        fields = ['date', 'mark_attendence']


class StudentAttendanceListSerializer(serializers.ModelSerializer):
    percentage = serializers.SerializerMethodField()
    total_attendance = serializers.SerializerMethodField()
    student = serializers.SerializerMethodField()
    class Meta:
        model = StudentAttendence
        fields = ['student', 'mark_attendence', 'percentage', 'total_attendance']


    def get_percentage(self, obj):
        year = datetime.date.today().year
        total_attendance = StudentAttendence.objects.filter(date__year=year,
            mark_attendence='P').count()
        total_school_days = 365
        attendence_percentage = (total_attendance / total_school_days) * 100
        return f"{round(attendence_percentage)}%"

    def get_student(self, obj):
        return obj.student

    def get_total_attendance(self, obj):
        year = datetime.date.today().year
        total_attendance = StudentAttendence.objects.filter(
            student=obj.student.id, date__year=year, mark_attendence__in=['A', 'P', 'L']).count()
        return total_attendance


class StudentListBySectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'class_enrolled', 'section']


class StudentAttendanceCreateSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField(required=False)
    class Meta:
        model = StudentAttendence
        fields = ['id', 'date', 'mark_attendence']

    def validate(self, data):
        if 'date' in data:
            try:
                # Attempt to parse the date string
                data['date'] = serializers.DateField().to_internal_value(data['date'])
            except serializers.ValidationError:
                raise serializers.ValidationError({"date": ["Date must be in YYYY-MM-DD format"]})
        return data


class StudentUserProfileSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    curriculum = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()
    age = serializers.SerializerMethodField()
    total_attendance = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = ['id', 'roll_no', 'name', 'image', 'class_enrolled', 'section', 'admission_date', 'dob', 'age', 'gender', 'religion', 'blood_group',
                  'school_fee','bus_fee', 'canteen_fee', 'other_fee', 'due_fee', 'total_fee', 'father_name', 'father_phone_number',
                  'father_occupation', 'mother_name', 'mother_phone_number', 'mother_occupation', 'email', 'permanent_address', 'curriculum',
                   'subjects', 'bus_number', 'bus_route', 'total_attendance']


    def get_curriculum(self,obj):
        return obj.curriculum if hasattr(obj, 'curriculum') else None

    def get_image(self, obj):
        if obj.image:
            if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
        return None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None

    def get_subjects(self, obj):
        try:
            curriculum = Curriculum.objects.get(curriculum_name=obj.curriculum, select_class=obj.class_enrolled)
            subject_data = Subjects.objects.filter(curriculum_id=curriculum.id)
            subjects = []
            for subject in subject_data:
                subjects.append(subject.primary_subject)
            return subjects or None
        except Curriculum.DoesNotExist as e:
            raise serializers.ValidationError(f"Error retrieving subjects: {str(e)}")


    def get_age(self, obj):
        if obj.dob:
            today = datetime.date.today()
            age = today.year - obj.dob.year - ((today.month, today.day) < (obj.dob.month, obj.dob.day))
            return age
        return None


    def get_total_attendance(self, obj):
        year = datetime.date.today().year
        total_attendance = StudentAttendence.objects.filter(
            student=obj.id, date__year=year, mark_attendence='P').count()
        return total_attendance


class AdminClassListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curriculum
        fields = ['select_class']


class AdminOptionalSubjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subjects
        fields = ['optional_subject']

class StudentAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAttendence
        fields = ['date','mark_attendence']