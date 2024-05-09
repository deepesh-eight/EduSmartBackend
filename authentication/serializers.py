from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from datetime import date
from EduSmart import settings
from constants import USER_TYPE_CHOICES, ROLE_CHOICES, ATTENDENCE_CHOICE, CATEGORY_TYPES
from content.models import Content
from teacher.serializers import CertificateSerializer, ImageFieldStringAndFile
from .models import User, AddressDetails, StaffUser, Certificate, StaffAttendence, EventsCalender
from django.core.exceptions import ValidationError as DjangoValidationError

class UserSignupSerializer(serializers.Serializer):
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
    state = serializers.CharField(required=False)
    country = serializers.CharField(required=True)
    pincode = serializers.CharField(required=True)


class AddressDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = AddressDetails
        fields = [
            'address_line_1', 'address_line_2', 'city', 'state', 'country', 'pincode'
        ]


class UsersListSerializer(serializers.ModelSerializer):
    address_details = AddressDetailsSerializer(many=True)

    class Meta:
        model = User
        fields = ['user_type', 'name', 'email', 'phone', 'is_active', 'address_details']


class UpdateProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = [
            'name', 'email', 'phone',
        ]

    def update(self, instance, validated_data):
        if validated_data.get('name'):
            instance.name = validated_data.get('name')
        if validated_data.get('email'):
            instance.email = validated_data.get('email')
        if validated_data.get('phone'):
            instance.phone = validated_data.get('phone')
        instance.save()
        return instance


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)


# Admin panel serializer
class StaffProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'name',
            'email',
            'phone',
            'designation',
            'is_email_verified',
            'is_active',
        ]


class StaffUpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'name',
            'phone',
            'designation'
        ]


class StaffSignupSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True)
    phone = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )
    school_id = serializers.CharField(max_length=255, required=True)


class NonTeachingStaffSerializers(serializers.Serializer):
    image = serializers.ImageField(required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    gender = serializers.CharField(required=True)
    dob = serializers.DateField(required=True)
    blood_group = serializers.CharField(required=False)
    religion = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )
    role = serializers.CharField(required=True)
    address = serializers.CharField(max_length=255, required=False)
    joining_date = serializers.DateField(required=True)
    ctc = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    certificate_files = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )

    def validate_certificate_files(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("Can't add more than 5 certificates.")

        for cert_file in value:
            if cert_file.size > 1048576:  # 1 MB
                raise serializers.ValidationError('Uploaded certificate size cannot exceed 1 MB.')

            try:
                cert_file.open()  # Ensure the file is open before further processing
                # Here you can perform additional validation if needed
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))

        return value


class NonTeachingStaffListSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    phone = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    class Meta:
        model = StaffUser
        fields = ['id', 'name', 'role', 'phone', 'email', 'image']

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None

    def get_image(self, obj):
        if obj.image:
            if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
        return None

    def get_name(self, obj):
        if obj.first_name and obj.last_name:
            return f'{obj.first_name} {obj.last_name}'

class NonTeachingStaffDetailSerializers(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    phone = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()

    class Meta:
        model = StaffUser
        fields = ['id', 'first_name', 'last_name', 'role', 'phone', 'email', 'image', 'dob', 'gender', 'religion', 'blood_group', 'address', 'joining_date',
                  'ctc', 'certificates']

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None

    def get_image(self, obj):
        if obj.image:
            if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
        return None


    def get_certificates(self, obj):
        # Fetch and serialize certificates associated with the user
        certificates = Certificate.objects.filter(user=obj.user)
        serializer = CertificateSerializer(certificates, many=True)
        return serializer.data

class NonTeachingStaffProfileSerializers(serializers.ModelSerializer):
    image = ImageFieldStringAndFile(required=False)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    gender = serializers.CharField(required=True)
    dob = serializers.DateField(required=True)
    blood_group = serializers.CharField(required=False)
    religion = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    phone = serializers.CharField(required=True)
    user_type = serializers.ChoiceField(
        choices=USER_TYPE_CHOICES
    )
    role = serializers.CharField(required=True)
    address = serializers.CharField(max_length=255, required=False)
    joining_date = serializers.DateField(required=True)
    ctc = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    certificate_files = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )


    class Meta:
        model = StaffUser
        fields = ['image', 'first_name', 'last_name', 'gender', 'dob', 'blood_group', 'religion', 'email', 'phone', 'user_type',
                  'role', 'address', 'address', 'joining_date', 'ctc','certificate_files']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        validated_data.pop('email', None)
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        return super().update(instance, validated_data)

    def validate_certificate_files(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("Can't add more than 5 certificates.")

        for cert_file in value:
            if cert_file.size > 1048576:  # 1 MB
                raise serializers.ValidationError('Uploaded certificate size cannot exceed 1 MB.')

            try:
                cert_file.open()  # Ensure the file is open before further processing
                # Here you can perform additional validation if needed
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e))

        return value


class StaffAttendanceSerializer(serializers.ModelSerializer):
    staff = serializers.CharField(required=True)
    mark_attendence = serializers.ChoiceField(choices=ATTENDENCE_CHOICE, required=True)

    class Meta:
        model = StaffAttendence
        fields = ['staff', 'mark_attendence']

    def create(self, validated_data):
        validated_data['date'] = date.today()
        student_id = validated_data.pop('staff')
        try:
            staff = StaffUser.objects.get(id=student_id)
        except StaffUser.DoesNotExist:
            raise serializers.ValidationError("Invalid staff ID.")

        # Check if attendance already marked for the user and today's date
        existing_attendance = StaffAttendence.objects.filter(staff=staff, date=validated_data['date']).exists()
        if existing_attendance:
            raise serializers.ValidationError("Attendance already marked for this staff today.")

        # Use the retrieved teacher object to create the attendance record
        teacher_attendance = StaffAttendence.objects.create(staff=staff, **validated_data)
        return teacher_attendance


class StaffAttendanceDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = StaffAttendence
        fields = ['date', 'mark_attendence']


class StaffAttendanceListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    class Meta:
        model = StaffUser
        fields = ['name', 'id', 'role']

    def get_name(self, obj):
        first_name = obj.first_name
        last_name = obj.last_name
        name = f"{first_name} {last_name}"
        if name:
            return name


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    default_error_messages = {
        'bad_token': 'Token is expired or invalid',
    }

    def validate(self, attrs):
        self.token = attrs['refresh']
        return attrs

    def save(self):
        try:
            refresh_token = RefreshToken(self.token)
            refresh_token.blacklist()
            access_token = refresh_token.access_token
            # if datetime.now() > access_token["exp"]:
            #     raise AuthenticationFailed(self.error_messages['bad_token'])
        except TokenError:
            raise AuthenticationFailed(self.error_messages['bad_token'])
        
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsCalender
        fields = ['is_one_day_event', 'is_event_calendar', 'title', 'description', 'event_image', 'start_time', 'end_time', 'start_date', 'end_date']

    def validate(self, data):
        if data['end_date'] < data['start_date']:
            raise serializers.ValidationError("End date must be after start date.")
        return data

class EventsCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsCalender
        fields = '__all__'


class StaffAttendanceFilterListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    id = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()
    class Meta:
        model = StaffAttendence
        fields = ['name', 'id', 'role', 'mark_attendence']

    def get_id(self, obj):
        return obj.staff.id

    def get_role(self, obj):
        return obj.staff.role

    def get_name(self, obj):
        first_name = obj.staff.first_name
        last_name = obj.staff.last_name
        name = f"{first_name} {last_name}"
        if name:
            return name
        else:
            None


class RecommendedBookCreateSerializer(serializers.ModelSerializer):
    # curriculum = serializers.SerializerMethodField()
    category = serializers.ChoiceField(
        choices=CATEGORY_TYPES
    )
    class Meta:
        model = Content
        fields = ['id','curriculum','content_media','content_media_link', 'category', 'image', 'content_type','content_name','content_creator','supporting_detail','description','is_recommended','classes','subject']