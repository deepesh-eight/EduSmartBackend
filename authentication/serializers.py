from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from django.utils import timezone
from pytz import timezone as pytz_timezone
from EduSmart import settings
from constants import USER_TYPE_CHOICES, ROLE_CHOICES, ATTENDENCE_CHOICE, CATEGORY_TYPES
from content.models import Content
from curriculum.models import Subjects, Curriculum
from student.models import StudentAttendence
from superadmin.models import SchoolProfile
from teacher.serializers import CertificateSerializer, ImageFieldStringAndFile
from utils import get_student_total_attendance
from .models import User, AddressDetails, StaffUser, Certificate, StaffAttendence, EventsCalender, ClassEvent, \
    ClassEventImage, EventImage, TimeTable, TeacherUser, StudentUser, InquiryForm
from django.core.exceptions import ValidationError as DjangoValidationError
from datetime import datetime, date


class CustomTimeField(serializers.TimeField):
    def to_internal_value(self, value):
        try:
            # Convert 12-hour time format to 24-hour time format
            if isinstance(value, str):
                value = datetime.strptime(value, '%I:%M %p').strftime('%H:%M:%S')
        except ValueError:
            raise serializers.ValidationError('Time has wrong format. Use hh:mm[:ss[.uuuuuu]] instead.')
        return super().to_internal_value(value)
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
    phone = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        ]
    )
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
    phone = serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        ]
    )
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
    experience = serializers.IntegerField(required=False)
    highest_qualification = serializers.CharField(max_length=255, required=False)

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
    # image = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()

    class Meta:
        model = StaffUser
        fields = ['id', 'first_name', 'last_name', 'role', 'phone', 'email', 'image', 'dob', 'gender', 'religion', 'blood_group', 'address', 'joining_date',
                  'ctc', 'certificates', 'experience', 'highest_qualification']

    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

    def get_email(self, obj):
        return obj.user.email if hasattr(obj, 'user') else None

    # def get_image(self, obj):
    #     if obj.image:
    #         if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
    #             return str(obj.image)
    #         else:
    #             return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
    #     return None


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
    # experience = serializers.IntegerField(required=False)
    # highest_qualification = serializers.CharField(max_length=255, required=False)


    class Meta:
        model = StaffUser
        fields = ['image', 'first_name', 'last_name', 'gender', 'dob', 'blood_group', 'religion', 'email', 'phone', 'user_type',
                  'role', 'address', 'address', 'joining_date', 'ctc','certificate_files']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', {})
        validated_data.pop('email', None)
        validated_data.pop('image', None)
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # Handle image separately to avoid re-assigning the URL
        image_data = validated_data.pop('image', None)
        if image_data:
            if hasattr(image_data, 'content_type') or ('blob.core.windows.net' not in image_data):
                instance.image = image_data
            else:
                # If the image_data is a URL, don't update the instance.image
                pass

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


class EventSerializer(serializers.Serializer):
    is_one_day_event = serializers.BooleanField(required=False)
    is_event_calendar = serializers.BooleanField(required=False)
    title = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    start_time = CustomTimeField(required=False)
    end_time = CustomTimeField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    event_image = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )

    # def validate(self, data):
    #     if data['end_date'] < data['start_date']:
    #         raise serializers.ValidationError("End date must be after start date.")
    #     return data

    def validate_event(self, value):
        if len(value) > 2:
            raise serializers.ValidationError("Can't add more than 2 images.")
        return value


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


class ClassEventCreateSerializer(serializers.Serializer):
    curriculum = serializers.CharField(required=True)
    select_class = serializers.CharField(required=True)
    section = serializers.CharField(required=True)
    date = serializers.DateField(required=True)
    start_time = CustomTimeField(required=False)
    end_time = CustomTimeField(required=False)
    title = serializers.CharField(required=True)
    discription = serializers.CharField(max_length=255)
    event_image = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )

    def validate_event_image(self, value):
        if len(value) > 2:
            raise serializers.ValidationError("Can't add more than 2 images.")
        return value


class ClassEventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassEvent
        fields = ['id', 'date', 'title', 'discription']


class ClassEventImageSerializer(serializers.ModelSerializer):
    # event_image= serializers.SerializerMethodField()
    class Meta:
        model = ClassEventImage
        fields = ['event_image']

    # def get_event_image(self, obj):
    #     if obj.event_image:
    #         return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.event_image)}'
    #     return None


class ClassEventDetailSerializer(serializers.ModelSerializer):
    curriculum = serializers.CharField(required=True)
    select_class = serializers.CharField(required=True)
    section = serializers.CharField(required=True)
    date = serializers.DateField(required=True)
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    title = serializers.CharField(required=True)
    discription = serializers.CharField(max_length=255)
    event_image = serializers.SerializerMethodField()

    class Meta:
        model = ClassEvent
        fields = ['id', 'curriculum', 'select_class', 'section', 'date', 'start_time', 'end_time', 'title', 'discription', 'event_image']

    def get_event_image(self, obj):
        event_image = ClassEventImage.objects.filter(class_event=obj.id)
        event_image_list = ClassEventImageSerializer(event_image, many=True)
        return event_image_list.data

    def get_start_time(self, obj):
        return obj.start_time.strftime("%I:%M %p")

    def get_end_time(self, obj):
        return obj.end_time.strftime("%I:%M %p")


class ClassEventUpdateSerializer(serializers.Serializer):
    curriculum = serializers.CharField(required=True)
    select_class = serializers.CharField(required=True)
    section = serializers.CharField(required=True)
    date = serializers.DateField(required=True)
    start_time = CustomTimeField(required=False)
    end_time = CustomTimeField(required=False)
    title = serializers.CharField(required=True)
    discription = serializers.CharField(max_length=255)
    event_image = serializers.ListField(
        child=serializers.FileField(),
        required=False
    )

    class Meta:
        model = ClassEvent

    def update(self, instance, validated_data):
        instance.curriculum = validated_data.get('curriculum', instance.curriculum)
        instance.select_class = validated_data.get('select_class', instance.select_class)
        instance.section = validated_data.get('section', instance.section)
        instance.date = validated_data.get('date', instance.date)
        instance.start_time = validated_data.get('start_time', instance.start_time)
        instance.end_time = validated_data.get('end_time', instance.end_time)
        instance.title = validated_data.get('title', instance.title)
        instance.discription = validated_data.get('discription', instance.discription)

        instance.save()

        return instance

    def validate_event_image(self, value):
        if len(value) > 2:
            raise serializers.ValidationError("Can't add more than 2 images.")
        return value


class AcademicCalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsCalender
        fields = ['id', 'is_event_calendar', 'start_date', 'end_date', 'title', 'description']


class EventListSerializer(serializers.ModelSerializer):
    event_name = serializers.SerializerMethodField()
    event_image = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    class Meta:
        model = EventsCalender
        fields = ['id', 'event_name', 'event_image', 'is_event_calendar', 'start_date', 'start_time', 'end_time', 'end_date', 'title', 'description']

    def get_event_name(self, obj):
        current_date_time_ist = timezone.localtime(timezone.now(), pytz_timezone('Asia/Kolkata'))
        current_date = current_date_time_ist.date()
        if obj.start_date == current_date:
            return "Today Event"
        else:
            return "Upcoming Event"

    def get_event_image(self, obj):
        if obj.event_image:
            if obj.event_image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.event_image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.event_image)}'
        return None

    def get_start_time(self, obj):
        if obj.start_date:
            return obj.start_time.strftime("%I:%M %p")

    def get_end_time(self, obj):
        if obj.end_date:
            return obj.start_time.strftime("%I:%M %p")


class EventImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventImage
        fields = ['event_image']


class EventDetailSerializer(serializers.ModelSerializer):
    event_image = serializers.SerializerMethodField()

    class Meta:
        model = EventsCalender
        fields = ['id', 'is_event_calendar', 'is_one_day_event', 'event_image', 'start_date', 'end_date', 'start_time', 'end_time', 'title', 'description']

    def get_event_image(self, obj):
        event_image = EventImage.objects.filter(event=obj.id)
        event_image_list = EventImageSerializer(event_image, many=True)
        return event_image_list.data


class TeacherEventListSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    class Meta:
        model = EventsCalender
        fields = ['id', 'start_date', 'end_date', 'title', 'description', 'start_time', 'end_time']

    def get_start_time(self, obj):
        if obj.start_date:
            return obj.start_time.strftime("%I:%M %p")

    def get_end_time(self, obj):
        if obj.end_date:
            return obj.start_time.strftime("%I:%M %p")



class TeacherEventDetailSerializer(serializers.ModelSerializer):
    event_image = serializers.SerializerMethodField()
    class Meta:
        model = EventsCalender
        fields = ['id', 'is_event_calendar', 'is_one_day_event', 'event_image', 'start_date', 'end_date', 'start_time', 'end_time', 'title', 'description']

    def get_event_image(self, obj):
        if obj.event_image:
            if obj.event_image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.event_image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.event_image)}'
        return None


class TeacherCalendarDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventsCalender
        fields = ['id', 'is_event_calendar', 'start_date', 'end_date', 'start_time', 'end_time', 'title', 'description']


class ExamScheduleListSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    # end_date = serializers.SerializerMethodField()
    exam_month = serializers.SerializerMethodField()
    class Meta:
        model = TimeTable
        fields = ['curriculum', 'class_name', 'class_section', 'exam_type', 'start_date', 'exam_month']

    def get_start_date(self, obj):
        data = obj.more_subject
        if data:
            for date in data:
                return date.get('date')
        else:
            return None

    # def get_end_date(self, obj):
    #     data = obj.more_subject
    #     if data:
    #         for date in data:
    #             end_data = date.get('date')
    #         return end_data
    #     else:
    #         return None

    def get_exam_month(self, obj):
        exam_month_str = obj.exam_month  # Assuming 'exm_month' is a date string

        exam_date = datetime.strptime(str(exam_month_str), "%Y-%m-%d")

        year = exam_date.year
        month_name = exam_date.strftime("%B")

        return f"{month_name}, {year}"


class ExamScheduleDetailSerializer(serializers.ModelSerializer):
    class_teacher = serializers.SerializerMethodField()
    exam_month = serializers.SerializerMethodField()

    class Meta:
        model = TimeTable
        fields = ['class_name', 'class_teacher', 'class_section', 'exam_type', 'exam_month', 'more_subject']

    def get_class_teacher(self, obj):
        teacher = TeacherUser.objects.get(role='class teacher', class_subject_section_details__0__curriculum=obj.curriculum, class_subject_section_details__0__class=obj.class_name,
                                             class_subject_section_details__0__section=obj.class_section)
        if teacher:
            return teacher.full_name
        else:
            None

    def get_exam_month(self, obj):
        exam_month_str = obj.exam_month  # Assuming 'exm_month' is a date string
        exam_date = datetime.strptime(str(exam_month_str), "%Y-%m-%d")
        month_name = exam_date.strftime("%B")
        return f"{month_name}"



class StudentInfoListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUser
        fields = ['id', 'name']

class StudentInfoDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    curriculum = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()
    total_attendance = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()

    # optional_subjects = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'image', 'class_enrolled', 'section', 'admission_date', 'dob', 'gender', 'religion',
                  'blood_group',
                  'school_fee', 'bus_fee', 'canteen_fee', 'other_fee', 'due_fee', 'total_fee', 'father_name',
                  'father_phone_number',
                  'father_occupation', 'mother_name', 'mother_phone_number', 'mother_occupation', 'email',
                  'permanent_address', 'curriculum',
                  'subjects', 'bus_number', 'bus_route', 'enrollment_no', 'roll_no', 'optional_subject', 'guardian_no', 'total_attendance',
                  'school_name']

    def get_curriculum(self, obj):
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

    def get_total_attendance(self, obj):
        student = obj.id
        year = date.today().year
        total_attendance = StudentAttendence.objects.filter(
            student=student, date__year=year, mark_attendence='P').count()
        return total_attendance

    def get_school_name(self, obj):
        School_name = SchoolProfile.objects.get(school_id=obj.user.school_id)
        if School_name:
            return School_name.school_name
        else:
            None


class InquirySerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    phone_number= serializers.CharField(
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="Phone number must be exactly 10 digits."
            )
        ]
    )
    e_mail = serializers.EmailField(required=True)

    class Meta:
        model = InquiryForm
        fields = ['name', 'phone_number', 'e_mail', 'description']
