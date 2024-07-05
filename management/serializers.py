import re

from rest_framework import serializers

from EduSmart import settings
from authentication.models import StaffUser, Certificate, TimeTable, TeacherUser, StudentUser, User
from curriculum.models import Curriculum
from management.models import Salary, SalaryFormat
from student.models import ExmaReportCard
from superadmin.models import SchoolProfile
from teacher.serializers import CertificateSerializer


class ManagementProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email')
    phone = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    school_id = serializers.SerializerMethodField()
    school_name = serializers.SerializerMethodField()
    curriculum = serializers.SerializerMethodField()
    school_website = serializers.SerializerMethodField()
    school_address = serializers.SerializerMethodField()
    school_about = serializers.SerializerMethodField()
    super_admin_mail = serializers.SerializerMethodField()

    class Meta:
        model = StaffUser
        fields = ['id', 'first_name', 'last_name', 'role', 'phone', 'email', 'image', 'dob', 'gender', 'religion',
                  'blood_group', 'address', 'joining_date',
                  'ctc', 'certificates', 'experience', 'highest_qualification', 'school_id', 'school_name', 'school_website',
                  'school_address', 'school_about', 'curriculum', 'super_admin_mail']

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

    def get_super_admin_mail(self, obj):
        return "support@edusmartai.com"

    def get_school_id(self, obj):
        return obj.user.school_id

    def get_school_name(self, obj):
        school = SchoolProfile.objects.get(school_id=obj.user.school_id)
        if school:
            return school.school_name
        else:
            None

    def get_school_website(self, obj):
        school = SchoolProfile.objects.get(school_id=obj.user.school_id)
        if school:
            return school.school_website
        else:
            None

    def get_school_address(self, obj):
        school = SchoolProfile.objects.get(school_id=obj.user.school_id)
        if school:
            return school.address
        else:
            None

    def get_school_about(self, obj):
        school = SchoolProfile.objects.get(school_id=obj.user.school_id)
        if school:
            return school.description
        else:
            None

    def get_curriculum(self, obj):
        curriculum = Curriculum.objects.filter(school_id=obj.user.school_id)
        data = []
        if curriculum:
            for curriculum_data in curriculum:
                data.append(curriculum_data.curriculum_name)
            return set(data)
        else:
            None


class TimeTableSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    exam_month = serializers.SerializerMethodField()

    class Meta:
        model = TimeTable
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'exam_type', 'start_date', 'exam_month']

    def get_start_date(self, obj):
        more_subjects = obj.more_subject
        if more_subjects:
            exam_dates = [subject['date'] for subject in more_subjects]
            return min(exam_dates)
        return None

    def get_exam_month(self, obj):
        return obj.exam_month.strftime("%B")


class TimeTableDetailViewSerializer(serializers.ModelSerializer):
    teacher = serializers.SerializerMethodField()
    class Meta:
        model = TimeTable
        fields = ['id', 'teacher', 'class_name', 'curriculum', 'class_section', 'exam_type', 'exam_month', 'more_subject']

    def get_teacher(self, obj):
        teacher = TeacherUser.objects.get(id=obj.teacher_id)
        if teacher:
            return teacher.full_name
        else:
            return None


class ExamReportCardSerializer(serializers.ModelSerializer):
    upload_date = serializers.SerializerMethodField()
    exam_month = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    roll_no = serializers.SerializerMethodField()
    class Meta:
        model = ExmaReportCard
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'exam_type', 'exam_month', 'upload_date', 'student_name', 'roll_no']

    def get_upload_date(self, obj):
        return obj.updated_at.date()

    def get_exam_month(self, obj):
        return obj.exam_month.strftime("%B")

    def get_student_name(self, obj):
        name, _ = self.split_student_data(obj.student_name)
        return name

    def get_roll_no(self, obj):
        _, roll_no = self.split_student_data(obj.student_name)
        return roll_no

    def split_student_data(self, student_data):
        pattern = r'^(.*?)-(.*?)$'
        match = re.match(pattern, student_data)
        if match:
            student_name = match.group(1).strip()
            roll_no = match.group(2).strip()
            return student_name, roll_no
        else:
            raise serializers.ValidationError("Input format is incorrect. Expected format: 'name-roll_no'.")


class StudentReportCardSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    roll_no = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    teacher_name = serializers.SerializerMethodField()
    father_name = serializers.SerializerMethodField()
    mother_name = serializers.SerializerMethodField()

    class Meta:
        model = ExmaReportCard
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'roll_no', 'student_id', 'student_name', 'father_name', 'mother_name', 'exam_type',
                 'marks_grades', 'total_marks', 'overall_grades', 'teacher_name']

    def get_upload_date(self, obj):
        return obj.updated_at.date()

    def get_exam_month(self, obj):
        return obj.exam_month.strftime("%B")

    def get_student_name(self, obj):
        name, _ = self.split_student_data(obj.student_name)
        return name

    def get_roll_no(self, obj):
        _, roll_no = self.split_student_data(obj.student_name)
        return roll_no

    def get_student_id(self, obj):
        if obj.student_name:
            _, roll_no = self.split_student_data(obj.student_name)
            student = StudentUser.objects.get(roll_no=roll_no)
            return student.id
        else:
            None

    def get_teacher_name(self, obj):
        if obj.student_name:
            _, roll_no = self.split_student_data(obj.student_name)
            student = StudentUser.objects.get(roll_no=roll_no)
            teacher = TeacherUser.objects.filter(class_subject_section_details__0__curriculum=student.curriculum,class_subject_section_details__0__class=student.class_enrolled).first()
            if teacher:
                return teacher.full_name
        else:
            return None

    def get_father_name(self, obj):
        if obj.student_name:
            _, roll_no = self.split_student_data(obj.student_name)
            student = StudentUser.objects.get(roll_no=roll_no)
            return student.father_name
        else:
            None

    def get_mother_name(self, obj):
        if obj.student_name:
            _, roll_no = self.split_student_data(obj.student_name)
            student = StudentUser.objects.get(roll_no=roll_no)
            return student.mother_name
        else:
            None

    def split_student_data(self, student_data):
        pattern = r'^(.*?)-(.*?)$'
        match = re.match(pattern, student_data)
        if match:
            student_name = match.group(1).strip()
            roll_no = match.group(2).strip()
            return student_name, roll_no
        else:
            raise serializers.ValidationError("Input format is incorrect. Expected format: 'name-roll_no'.")


class AddSalarySerializer(serializers.ModelSerializer):
    department = serializers.CharField(required=True)
    designation = serializers.CharField(required=True)
    joining_date = serializers.DateField(required=True)
    pan_no = serializers.CharField(required=True)
    total_salary = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    in_hand_salary = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    basic_salary = serializers.DecimalField(max_digits=16, decimal_places=2,  required=True)
    hra = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    other_allowances = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    deducted_salary = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    professional_tax = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    tds = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    epf = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    other_deduction = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    incentive = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    net_payable_amount = serializers.DecimalField(max_digits=16, decimal_places=2,required=True)
    bank_name = serializers.CharField(required=True)
    account_type = serializers.CharField(required=True)
    ifsc_code = serializers.CharField(required=True)
    account_number = serializers.CharField(required=True)
    field_name = serializers.ListField(child=serializers.CharField(), required=False)
    field_amount = serializers.ListField(child=serializers.CharField(), required=False)


    class Meta:
        model = Salary
        fields = [
            'department', 'designation', 'name', 'joining_date', 'pan_no',
            'total_salary', 'in_hand_salary', 'basic_salary', 'hra',
            'other_allowances', 'deducted_salary', 'professional_tax', 'tds',
            'epf', 'other_deduction', 'incentive', 'net_payable_amount',
            'bank_name', 'account_type', 'ifsc_code', 'account_number', 'field_name', 'field_amount'
        ]

    def create(self, validated_data):
        field_name_data = validated_data.pop('field_name', [])
        field_amount_data = validated_data.pop('field_amount', [])

        salary_structure = Salary.objects.create(**validated_data)

        max_index = max(len(field_name_data), len(field_amount_data))

        for index in range(max_index):
            field_name = field_name_data[index] if index < len(field_name_data) else None
            field_amount = field_amount_data[index] if index < len(field_amount_data) else None

            SalaryFormat.objects.create(
                salary_structure=salary_structure,
                field_name=field_name.strip() if field_name else None,
                field_amount=field_amount.strip() if field_amount else None
            )

        return salary_structure

    def validate_pan_no(self, value):
        pattern = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]$')
        if not pattern.match(value):
            raise serializers.ValidationError("Invalid PAN number format. It should be in the format ABCDE1234F.")
        return value

    def validate_ifsc_code(self, value):
        # Regular expression to match IFSC format: four letters, seven digits
        pattern = re.compile(r'^[A-Z]{4}[0-9]{7}$')
        if not pattern.match(value):
            raise serializers.ValidationError("Invalid IFSC code format. It should be in the format ABCD0123456.")
        return value

    def validate_account_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Account number must be numeric.")
        if len(value) < 9 or len(value) > 18:
            raise serializers.ValidationError("Account number must be between 9 and 18 digits.")
        return value


class SalaryDetailSerializer(serializers.ModelSerializer):
    staff_name = serializers.SerializerMethodField()
    staff_id = serializers.SerializerMethodField()
    institute_name = serializers.SerializerMethodField()
    class Meta:
        model = Salary
        fields = [
            'institute_name', 'department', 'designation', 'name', 'joining_date', 'pan_no',
            'total_salary', 'in_hand_salary', 'basic_salary', 'hra',
            'other_allowances', 'deducted_salary', 'professional_tax', 'tds',
            'epf', 'other_deduction', 'incentive', 'net_payable_amount',
            'bank_name', 'account_type', 'ifsc_code', 'account_number', 'staff_name', 'staff_id'
        ]

    def get_institute_name(self, obj):
        try:
            teaching_staff = TeacherUser.objects.get(user=obj.name)
            user = User.objects.get(id=teaching_staff.user.id)
            school = SchoolProfile.objects.get(school_id=user.school_id)
            return f"{school.school_name} {school.city} {school.state}"
        except TeacherUser.DoesNotExist:
            pass

        try:
            non_teaching_staff = StaffUser.objects.get(user=obj.name)
            user = User.objects.get(id=non_teaching_staff.user.id)
            school = SchoolProfile.objects.get(school_id=user.school_id)
            return f"{school.school_name} {school.city} {school.state}"
        except StaffUser.DoesNotExist:
            pass
        return None

    def get_staff_name(self, obj):
        try:
            teaching_staff = TeacherUser.objects.get(user=obj.name)
            return teaching_staff.full_name
        except TeacherUser.DoesNotExist:
            pass

        try:
            non_teaching_staff = StaffUser.objects.get(user=obj.name)
            return f"{non_teaching_staff.first_name} {non_teaching_staff.last_name}"
        except StaffUser.DoesNotExist:
            pass
        return None

    def get_staff_id(self, obj):
        try:
            teaching_staff = TeacherUser.objects.get(user=obj.name)
            return teaching_staff.id
        except TeacherUser.DoesNotExist:
            pass

        try:
            non_teaching_staff = StaffUser.objects.get(user=obj.name)
            return non_teaching_staff.id
        except StaffUser.DoesNotExist:
            pass
        return None


class SalaryUpdateSerializer(serializers.ModelSerializer):
    department = serializers.CharField(required=True)
    designation = serializers.CharField(required=True)
    joining_date = serializers.DateField(required=True)
    pan_no = serializers.CharField(required=True)
    total_salary = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    in_hand_salary = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    basic_salary = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    hra = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    other_allowances = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    deducted_salary = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    professional_tax = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    tds = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    epf = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    other_deduction = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    incentive = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    net_payable_amount = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    bank_name = serializers.CharField(required=True)
    account_type = serializers.CharField(required=True)
    ifsc_code = serializers.CharField(required=True)
    account_number = serializers.CharField(required=True)
    field_name = serializers.ListField(child=serializers.CharField(), required=False)
    field_amount = serializers.ListField(child=serializers.CharField(), required=False)
    class Meta:
        model = Salary
        fields = [
            'department', 'designation', 'name', 'joining_date', 'pan_no',
            'total_salary', 'in_hand_salary', 'basic_salary', 'hra',
            'other_allowances', 'deducted_salary', 'professional_tax', 'tds',
            'epf', 'other_deduction', 'incentive', 'net_payable_amount',
            'bank_name', 'account_type', 'ifsc_code', 'account_number', 'field_name', 'field_amount'
        ]

    def update(self, instance, validated_data):
        # Update the Salary instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        request = self.context.get('request')
        if not request:
            raise ValueError("Request is not in context")
        field_name = []
        field_amount = []

        for key in request.data.keys():
            if key.startswith('field_name'):
                field_name.append(request.data[key])
            if key.startswith('field_amount'):
                field_amount.append(request.data[key])

        if not field_name or not field_amount:
            raise ValueError("field_name or field_amount subjects are missing")

        SalaryFormat.objects.filter(salary_structure=instance.id).delete()

        for name, amount in zip(field_name, field_amount):
            SalaryFormat.objects.create(
                salary_structure=instance,
                field_name=name.strip() if amount else None,
                field_amount=amount.strip() if amount else None
            )

        return instance

        # instance.salary_structure.all().delete()
        #
        # # Re-create SalaryFormat related objects
        # max_index = max(len(field_name_data), len(field_amount_data))
        # for index in range(max_index):
        #     field_name = field_name_data[index] if index < len(field_name_data) else None
        #     field_amount = field_amount_data[index] if index < len(field_amount_data) else None
        #
        #     SalaryFormat.objects.create(
        #         salary_structure=instance,
        #         field_name=field_name.strip() if field_name else None,
        #         field_amount=field_amount.strip() if field_amount else None
        #     )
        #
        # return instance