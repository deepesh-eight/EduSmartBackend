import datetime
import re

from rest_framework import serializers

from EduSmart import settings
from authentication.models import StudentUser, User, TimeTable, TeacherUser, ClassEvent, DayReview
from authentication.serializers import AddressDetailsSerializer, CustomTimeField
from bus.models import Route, Bus
from constants import USER_TYPE_CHOICES, GENDER_CHOICES, RELIGION_CHOICES, CLASS_CHOICES, BLOOD_GROUP_CHOICES, \
    ATTENDENCE_CHOICE
from content.models import Content
from curriculum.models import Curriculum, Subjects
from student.models import StudentAttendence, ExmaReportCard, StudentMaterial, ZoomLink, ConnectWithTeacher


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
    bus_number = serializers.CharField(required=False)
    bus_route = serializers.IntegerField(required=False)
    enrollment_no = serializers.CharField(default='')
    roll_no = serializers.CharField(default='')
    guardian_no = serializers.CharField(default='')
    optional_subject = serializers.CharField(default='')
    current_address = serializers.CharField(max_length=255, required=False, default='')


class StudentDetailSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    email = serializers.SerializerMethodField()
    curriculum = serializers.SerializerMethodField()
    subjects = serializers.SerializerMethodField()
    bus_number = serializers.SerializerMethodField()
    bus_route = serializers.SerializerMethodField()
    bus_id = serializers.SerializerMethodField()
    bus_route_id = serializers.SerializerMethodField()
    # optional_subjects = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'image', 'class_enrolled', 'section', 'admission_date', 'dob', 'gender', 'religion', 'blood_group',
                  'school_fee','bus_fee', 'canteen_fee', 'other_fee', 'due_fee', 'total_fee', 'father_name', 'father_phone_number',
                  'father_occupation', 'mother_name', 'mother_phone_number', 'mother_occupation', 'email', 'permanent_address', 'curriculum',
                   'subjects', 'bus_number', 'bus_id', 'bus_route', 'bus_route_id', 'enrollment_no', 'roll_no', 'optional_subject', 'guardian_no', 'current_address']


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

    def get_bus_number(self, obj):
        bus_data = Bus.objects.get(id=obj.bus_number.id)
        if bus_data:
            return bus_data.bus_number

    def get_bus_route(self, obj):
        route_data = Route.objects.get(id=obj.bus_route.id)
        if route_data:
            return route_data.name

    def get_bus_id(self, obj):
        bus = Bus.objects.get(id=obj.bus_number.id)
        if bus:
            return bus.id
        else:
            None

    def get_bus_route_id(self, obj):
        route = Route.objects.get(id=obj.bus_route.id)
        if route:
            return route.id
        else:
            None

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
    current_address = serializers.CharField(max_length=255, required=False)
    bus_number = serializers.CharField(required=False)
    bus_route = serializers.CharField(required=False)
    guardian_no = serializers.CharField(default='')
    optional_subject = serializers.CharField(default='')


    class Meta:
        model = StudentUser
        fields = ['name', 'email', 'user_type', 'dob', 'image', 'father_name', 'father_phone_number', 'father_occupation', 'mother_name',
                  'mother_occupation', 'mother_phone_number', 'gender', 'admission_date', 'school_fee', 'bus_fee', 'canteen_fee', 'other_fee',
                  'due_fee', 'total_fee', 'religion', 'blood_group', 'class_enrolled', 'section', 'curriculum', 'permanent_address', 'bus_number',
                  'bus_route', 'guardian_no', 'optional_subject', 'current_address']

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

        # Update bus_number
        bus_number = validated_data.pop('bus_number', None)
        if bus_number:
            try:
                bus = Bus.objects.get(id=bus_number)
                instance.bus_number = bus
            except Bus.DoesNotExist:
                raise serializers.ValidationError({"bus_number": "Bus with this number does not exist."})

        # Update bus_route
        bus_route_id = validated_data.pop('bus_route', None)
        if bus_route_id:
            try:
                bus_route = Route.objects.get(id=bus_route_id)
                instance.bus_route = bus_route
            except Route.DoesNotExist:
                raise serializers.ValidationError({"bus_route": "Route with this ID does not exist."})

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance

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
    bus_number = serializers.SerializerMethodField()
    bus_route = serializers.SerializerMethodField()

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

    def get_bus_number(self, obj):
        bus_data = Bus.objects.get(id=obj.bus_number.id)
        if bus_data:
            return bus_data.bus_number

    def get_bus_route(self, obj):
        route_data = Route.objects.get(id=obj.bus_route.id)
        if route_data:
            return route_data.name

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


class StudentTimeTableListSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeTable
        fields = ['exam_type', 'more_subject']


class StudentReportCardListSerializer(serializers.ModelSerializer):
    father_name = serializers.SerializerMethodField()
    mother_name = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    roll_no = serializers.SerializerMethodField()

    class Meta:
        model = ExmaReportCard
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'roll_no', 'student_id', 'student_name', 'exam_type',
                 'marks_grades', 'total_marks', 'overall_grades', 'father_name', 'mother_name',
                  'teacher_name']

    def get_father_name(self, obj):
        student = obj.student_name
        roll_no = re.sub(r'\D', '', student)
        father_name = StudentUser.objects.get(roll_no=roll_no)
        return father_name.father_name

    def get_mother_name(self, obj):
        student = obj.student_name
        roll_no = re.sub(r'\D', '', student)
        father_name = StudentUser.objects.get(roll_no=roll_no)
        return father_name.mother_name

    def get_teacher_name(self, obj):
        class_name = obj.class_name
        if class_name:
            teacher = TeacherUser.objects.filter(class_subject_section_details__0__class=class_name).first()
            if teacher:
                return teacher.full_name
        return None

    def get_student_id(self, obj):
        student = obj.student_name
        roll_no = re.sub(r'\D', '', student)
        student_id = StudentUser.objects.get(roll_no=roll_no)
        return student_id.id

    def get_student_name(self, obj):
        student = obj.student_name
        student_name = re.search(r'[a-zA-Z\s]+', student).group().strip()
        return student_name

    def get_roll_no(self, obj):
        student = obj.student_name
        roll_no = re.sub(r'\D', '', student)
        return roll_no


class StudentStudyMaterialListSerializer(serializers.ModelSerializer):
    upload_content = serializers.SerializerMethodField()
    class Meta:
        model = StudentMaterial
        fields = ['id', 'class_name', 'section', 'subject', 'curriculum', 'upload_link', 'title', 'discription', 'upload_content', 'content_type']

    def get_upload_content(self, obj):
        if obj.upload_content:
            if obj.upload_content.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.upload_content)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.upload_content)}'
        return None


class StudentZoomLinkSerializer(serializers.ModelSerializer):
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()

    class Meta:
        model = ZoomLink
        fields = ['class_name', 'curriculum', 'section', 'subject', 'date', 'start_time', 'end_time', 'zoom_link']

    def get_start_time(self, obj):
        return obj.start_time.strftime("%I:%M %p")

    def get_end_time(self, obj):
        return obj.end_time.strftime("%I:%M %p")


class StudentContentListSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    content_media = serializers.SerializerMethodField()
    class Meta:
        model = Content
        fields = ['id','curriculum','content_media', 'image', 'content_media_link','content_type', 'category', 'content_name','content_creator','supporting_detail','description','is_recommended','classes','subject']

    def get_image(self, obj):
        if obj.image:
            if obj.image.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.image)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.image)}'
        return None

    def get_content_media(self, obj):
        if obj.content_media:
            if obj.content_media.name.startswith(settings.base_url + settings.MEDIA_URL):
                return str(obj.content_media)
            else:
                return f'{settings.base_url}{settings.MEDIA_URL}{str(obj.content_media)}'
        return None


class StudentClassEventListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassEvent
        fields = ['id', 'date', 'title', 'discription']


class StudentDayReviewDetailSerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()

    class Meta:
        model = DayReview
        fields = ['id', 'teacher_name', 'subject', 'discription']

    def get_teacher_name(self, obj):
        class_name = obj.class_name
        section = obj.section
        curriculum = obj.curriculum
        subject = obj.subject

        # Filter TeacherUser objects based on the provided criteria
        teacher_data = TeacherUser.objects.filter(class_subject_section_details__0__class=class_name,
                                                  class_subject_section_details__0__section=section,
                                                  class_subject_section_details__0__curriculum=curriculum,
                                                  class_subject_section_details__0__subject=subject)

        if teacher_data.exists():
            return teacher_data[0].full_name
        else:
            return None


class StudentSubjectListSerializer(serializers.ModelSerializer):
    subject = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = ['id', 'subject', 'optional_subject']

    def get_subject(self, obj):
        try:
            curriculum = Curriculum.objects.get(curriculum_name=obj.curriculum, select_class=obj.class_enrolled)
            subject_data = Subjects.objects.filter(curriculum_id=curriculum.id)
            subjects = []
            for subject in subject_data:
                subjects.append(subject.primary_subject)
            return subjects or None
        except Curriculum.DoesNotExist as e:
            raise serializers.ValidationError(f"Error retrieving subjects: {str(e)}")


class ConnectWithTeacherSerializer(serializers.Serializer):
    subject = serializers.CharField(required=True)
    start_time = CustomTimeField(required=False)
    end_time = CustomTimeField(required=False)


class ChatHistorySerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    class Meta:
        model = ConnectWithTeacher
        fields = ['id', 'teacher_name', 'class_name', 'section', 'subject']

    def get_teacher_name(self, obj):
        teacher_name = TeacherUser.objects.get(id=obj.teacher.id)
        if teacher_name:
            return teacher_name.full_name
        else:
            None