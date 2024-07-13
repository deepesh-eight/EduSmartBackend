import re
from calendar import monthrange
from datetime import datetime

from rest_framework import serializers

from EduSmart import settings
from authentication.models import StaffUser, Certificate, TimeTable, TeacherUser, StudentUser, User, TeacherAttendence, \
    StaffAttendence
from curriculum.models import Curriculum
from management.models import Salary, SalaryFormat, Fee, FeeFormat, DueFeeDetail
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
                  'ctc', 'certificates', 'experience', 'highest_qualification', 'school_id', 'school_name',
                  'school_website',
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
        fields = ['id', 'teacher', 'class_name', 'curriculum', 'class_section', 'exam_type', 'exam_month',
                  'more_subject']

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
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'exam_type', 'exam_month', 'upload_date',
                  'student_name', 'roll_no']

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
        fields = ['id', 'class_name', 'curriculum', 'class_section', 'roll_no', 'student_id', 'student_name',
                  'father_name', 'mother_name', 'exam_type',
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
            teacher = TeacherUser.objects.filter(class_subject_section_details__0__curriculum=student.curriculum,
                                                 class_subject_section_details__0__class=student.class_enrolled).first()
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
    master_days = serializers.IntegerField(required=True)
    total_working_days = serializers.IntegerField(required=True)
    leave_days = serializers.IntegerField(required=True)

    class Meta:
        model = Salary
        fields = [
            'department', 'designation', 'name', 'joining_date', 'pan_no',
            'total_salary', 'in_hand_salary', 'basic_salary', 'hra',
            'other_allowances', 'deducted_salary', 'professional_tax', 'tds',
            'epf', 'other_deduction', 'incentive', 'net_payable_amount',
            'bank_name', 'account_type', 'ifsc_code', 'account_number', 'field_name', 'field_amount',
            'master_days', 'total_working_days', 'leave_days'
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
            'total_salary', 'in_hand_salary', 'basic_salary', 'hra', 'master_days', 'total_working_days', 'leave_days',
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
    department = serializers.CharField(required=False)
    designation = serializers.CharField(required=False)
    joining_date = serializers.DateField(required=False)
    pan_no = serializers.CharField(required=False)
    total_salary = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    in_hand_salary = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    basic_salary = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    hra = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    other_allowances = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    deducted_salary = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    professional_tax = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    tds = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    epf = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    other_deduction = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    incentive = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    net_payable_amount = serializers.DecimalField(max_digits=16, decimal_places=2, required=False)
    bank_name = serializers.CharField(required=False)
    account_type = serializers.CharField(required=False)
    ifsc_code = serializers.CharField(required=False)
    account_number = serializers.CharField(required=False)
    field_name = serializers.ListField(child=serializers.CharField(), required=False)
    field_amount = serializers.ListField(child=serializers.CharField(), required=False)
    master_days = serializers.IntegerField(required=False)
    total_working_days = serializers.IntegerField(required=False)
    leave_days = serializers.IntegerField(required=False)

    class Meta:
        model = Salary
        fields = [
            'department', 'designation', 'name', 'joining_date', 'pan_no',
            'total_salary', 'in_hand_salary', 'basic_salary', 'hra',
            'other_allowances', 'deducted_salary', 'professional_tax', 'tds',
            'epf', 'other_deduction', 'incentive', 'net_payable_amount',
            'bank_name', 'account_type', 'ifsc_code', 'account_number', 'field_name', 'field_amount',
            'master_days', 'total_working_days', 'leave_days'
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


class AddFeeSerializer(serializers.ModelSerializer):
    curriculum = serializers.CharField(required=True)
    class_name = serializers.CharField(required=True)
    payment_type = serializers.CharField(required=True)
    instalment_amount = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    no_of_instalment = serializers.IntegerField(required=True)
    school_fee = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    total_fee = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    bus_fee = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    canteen_fee = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    miscellaneous_fee = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    min_paid_amount = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    max_total_remain = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    field_name = serializers.ListField(child=serializers.CharField(), required=False)
    field_amount = serializers.ListField(child=serializers.CharField(), required=False)
    due_type = serializers.ListField(child=serializers.CharField(), required=False)
    due_amount = serializers.ListField(child=serializers.CharField(), required=False)
    last_due_date = serializers.ListField(child=serializers.CharField(), required=False)
    late_fee = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Fee
        fields = [
            'curriculum', 'name', 'class_name', 'payment_type', 'instalment_amount', 'no_of_instalment', 'school_fee',
            'total_fee',
            'bus_fee', 'canteen_fee', 'miscellaneous_fee', 'min_paid_amount', 'max_total_remain', 'field_name',
            'field_amount',
            'due_type', 'due_amount', 'last_due_date', 'late_fee']

    def create(self, validated_data):
        field_name_data = validated_data.pop('field_name', [])
        field_amount_data = validated_data.pop('field_amount', [])
        due_type_data = validated_data.pop('due_type', [])
        due_amount_data = validated_data.pop('due_amount', [])
        last_due_date_data = validated_data.pop('last_due_date', [])
        late_fee_data = validated_data.pop('late_fee', [])

        fee_structure = Fee.objects.create(**validated_data)

        for field_name, field_amount in zip(field_name_data, field_amount_data):
            FeeFormat.objects.create(
                fee_structure=fee_structure,
                field_name=field_name,
                field_amount=field_amount
            )

        for due_type, due_amount, last_due_date, late_fee in zip(due_type_data, due_amount_data, last_due_date_data,
                                                                 late_fee_data):
            DueFeeDetail.objects.create(
                fee_structure=fee_structure,
                due_type=due_type,
                due_amount=due_amount,
                last_due_date=last_due_date,
                late_fee=late_fee
            )

        return fee_structure


class FeeFormatSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeeFormat
        fields = ['field_name', 'field_amount']


class DueFeeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = DueFeeDetail
        fields = ['due_type', 'due_amount', 'last_due_date', 'late_fee']


class FeeListSerializer(serializers.ModelSerializer):
    fee_structure = FeeFormatSerializer(many=True, read_only=True)
    due_fee_detail = DueFeeDetailSerializer(many=True, read_only=True)
    name = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()

    class Meta:
        model = Fee
        fields = ['id', 'school_id', 'curriculum', 'name', 'class_name', 'section', 'payment_type', 'instalment_amount',
                  'no_of_instalment', 'school_fee', 'total_fee', 'bus_fee', 'canteen_fee',
                  'miscellaneous_fee', 'min_paid_amount', 'max_total_remain',
                  'fee_structure', 'due_fee_detail']

    def get_name(self, obj):
        if obj.name:
            student = StudentUser.objects.get(id=obj.name.id)
            return student.name
        else:
            None

    def get_section(self, obj):
        if obj.name:
            student = StudentUser.objects.get(id=obj.name.id)
            return student.section
        else:
            None


class FeeUpdateSerializer(serializers.ModelSerializer):
    curriculum = serializers.CharField(required=True)
    class_name = serializers.CharField(required=True)
    payment_type = serializers.CharField(required=True)
    instalment_amount = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    no_of_instalment = serializers.IntegerField(required=True)
    school_fee = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    total_fee = serializers.DecimalField(max_digits=16, decimal_places=2, required=True)
    bus_fee = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    canteen_fee = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    miscellaneous_fee = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    min_paid_amount = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    max_total_remain = serializers.DecimalField(max_digits=16, decimal_places=2, default=0.0)
    field_name = serializers.ListField(child=serializers.CharField(), required=False)
    field_amount = serializers.ListField(child=serializers.CharField(), required=False)
    due_type = serializers.ListField(child=serializers.CharField(), required=False)
    due_amount = serializers.ListField(child=serializers.CharField(), required=False)
    last_due_date = serializers.ListField(child=serializers.CharField(), required=False)
    late_fee = serializers.ListField(child=serializers.CharField(), required=False)

    class Meta:
        model = Fee
        fields = [
            'curriculum', 'name', 'class_name', 'payment_type', 'instalment_amount', 'no_of_instalment', 'school_fee',
            'total_fee',
            'bus_fee', 'canteen_fee', 'miscellaneous_fee', 'min_paid_amount', 'max_total_remain', 'field_name',
            'field_amount',
            'due_type', 'due_amount', 'last_due_date', 'late_fee']

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
        due_type = []
        due_amount = []
        last_due_date = []
        late_fee = []

        for key in request.data.keys():
            if key.startswith('field_name'):
                field_name.append(request.data[key])
            if key.startswith('field_amount'):
                field_amount.append(request.data[key])
            if key.startswith('due_type'):
                due_type.append(request.data[key])
            if key.startswith('due_amount'):
                due_amount.append(request.data[key])
            if key.startswith('last_due_date'):
                last_due_date.append(request.data[key])
            if key.startswith('late_fee'):
                late_fee.append(request.data[key])

        if not field_name or not field_amount:
            raise ValueError("field_name or field_amount subjects are missing")

        FeeFormat.objects.filter(fee_structure=instance.id).delete()
        DueFeeDetail.objects.filter(fee_structure=instance.id).delete()

        for name, amount in zip(field_name, field_amount):
            FeeFormat.objects.create(
                fee_structure=instance,
                field_name=name.strip() if amount else None,
                field_amount=amount.strip() if amount else None
            )
        for due_type, due_amount, last_due_date, late_fee in zip(due_type, due_amount, last_due_date,late_fee):
            DueFeeDetail.objects.create(
                fee_structure=instance,
                due_type=due_type,
                due_amount=due_amount,
                last_due_date=last_due_date,
                late_fee=late_fee
            )
        return instance


class FeeDetailSerializer(serializers.ModelSerializer):
    fee_structure = FeeFormatSerializer(many=True, read_only=True)
    due_fee_detail = DueFeeDetailSerializer(many=True, read_only=True)
    student_name = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()
    joining_date = serializers.SerializerMethodField()
    student_id = serializers.SerializerMethodField()
    institute_name = serializers.SerializerMethodField()
    class Meta:
        model = Fee
        fields = ['curriculum', 'class_name', 'student_name', 'student_id', 'section', 'joining_date', 'curriculum', 'institute_name',
                  'payment_type', 'instalment_amount', 'no_of_instalment', 'school_fee', 'total_fee',
                  'bus_fee', 'canteen_fee', 'miscellaneous_fee', 'min_paid_amount', 'max_total_remain', 'fee_structure', 'due_fee_detail'
                  ]

    def get_student_name(self, obj):
        if obj.name:
            student = StudentUser.objects.get(id=obj.name.id)
            return student.name
        else:
            None

    def get_section(self, obj):
        if obj.name:
            student = StudentUser.objects.get(id=obj.name.id)
            return student.section
        else:
            None

    def get_joining_date(self, obj):
        if obj.name:
            student = StudentUser.objects.get(id=obj.name.id)
            return student.admission_date
        else:
            None

    def get_student_id(self, obj):
        if obj.name:
            student = StudentUser.objects.get(id=obj.name.id)
            return student.id
        else:
            None

    def get_institute_name(self, obj):
        if obj.name:
            student = StudentUser.objects.get(user=obj.name.user)
            user = User.objects.get(id=student.user.id)
            school = SchoolProfile.objects.get(school_id=user.school_id)
            return f"{school.school_name} {school.city} {school.state}"
        else:
            None


class StudentListsSerializer(serializers.ModelSerializer):
    curriculum = serializers.SerializerMethodField()
    class_name = serializers.SerializerMethodField()
    section = serializers.SerializerMethodField()
    class_teacher = serializers.SerializerMethodField()
    total_students = serializers.SerializerMethodField()

    class Meta:
        model = TeacherUser
        fields = ['class_teacher', 'curriculum', 'class_name', 'section', 'total_students']

    def get_curriculum(self, obj):
        if obj.role == 'class teacher':
            class_teacher = obj.class_subject_section_details[0].get('curriculum')
            return class_teacher
        else:
            None

    def get_class_name(self, obj):
        if obj.role == 'class teacher':
            class_teacher = obj.class_subject_section_details[0].get('class')
            return class_teacher
        else:
            None

    def get_section(self, obj):
        if obj.role == 'class teacher':
            class_teacher = obj.class_subject_section_details[0].get('section')
            return class_teacher
        else:
            None

    def get_class_teacher(self, obj):
        if obj.role == 'class teacher':
            class_teacher = obj.full_name
            return class_teacher
        else:
            None

    def get_total_students(self, obj):
        if obj.role == 'class teacher':
            curriculum = obj.class_subject_section_details[0].get('curriculum')
            class_name = obj.class_subject_section_details[0].get('class')
            section = obj.class_subject_section_details[0].get('section')
            return StudentUser.objects.filter(curriculum=curriculum, class_enrolled=class_name, section=section, user__is_active=True).count()
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if instance.role != 'class teacher':
            # Remove fields if the user is not a class teacher
            representation.pop('curriculum', None)
            representation.pop('class_name', None)
            representation.pop('section', None)
            representation.pop('class_teacher', None)
            if all(value is None for value in representation.values()):
                return None
        return representation


class StudentFilterListSerializer(serializers.ModelSerializer):
    fee_type = serializers.SerializerMethodField()
    total_fee = serializers.SerializerMethodField()
    paid_fee = serializers.SerializerMethodField()
    due_fee = serializers.SerializerMethodField()
    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'roll_no', 'admission_date', 'fee_type', 'total_fee', 'paid_fee', 'due_fee']

    def get_fee_type(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.payment_type
        except Fee.DoesNotExist:
            return None

    def get_total_fee(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.total_fee
        except Fee.DoesNotExist:
            return None

    def get_paid_fee(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.total_fee # Here i need to add paid fee field
        except Fee.DoesNotExist:
            return None

    def get_due_fee(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.total_fee-10000 # In the place of 10000 we need to write paid_fee
        except Fee.DoesNotExist:
            return None


class StudentDetailSerializer(serializers.ModelSerializer):
    institute_name = serializers.SerializerMethodField()
    fee_type = serializers.SerializerMethodField()
    due_type = serializers.SerializerMethodField()
    school_fee = serializers.SerializerMethodField()
    total_due_amount = serializers.SerializerMethodField()
    bus_fee = serializers.SerializerMethodField()
    monthly_instalment = serializers.SerializerMethodField()
    canteen_fee = serializers.SerializerMethodField()
    no_of_instalment = serializers.SerializerMethodField()
    miscellaneous_fee = serializers.SerializerMethodField()
    # next_due_amount = serializers.SerializerMethodField()
    # last_amount_paid = serializers.SerializerMethodField()
    # next_due_date = serializers.SerializerMethodField()
    # last_paid_date = serializers.SerializerMethodField()
    late_fee = serializers.SerializerMethodField()
    # fee_paid_by_student = serializers.SerializerMethodField()
    # total_due_to_pay = serializers.SerializerMethodField()
    total_fee = serializers.SerializerMethodField()


    class Meta:
        model = StudentUser
        fields = ['id', 'name', 'roll_no', 'curriculum', 'class_enrolled', 'section', 'admission_date', 'institute_name', 'fee_type',
                  'due_type', 'school_fee', 'total_due_amount', 'bus_fee', 'monthly_instalment', 'no_of_instalment', 'canteen_fee',
                  'miscellaneous_fee', 'late_fee', 'total_fee']

    def get_institute_name(self, obj):
        if obj.name:
            student = StudentUser.objects.get(user=obj.user)
            user = User.objects.get(id=student.user.id)
            school = SchoolProfile.objects.get(school_id=user.school_id)
            return f"{school.school_name} {school.city} {school.state}"
        else:
            None

    def get_fee_type(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.payment_type
        except Fee.DoesNotExist:
            return None

    def get_due_type(self, obj):
        try:
            fee_due_type = []
            fee_detail = Fee.objects.get(name=obj)
            fee = DueFeeDetail.objects.filter(fee_structure=fee_detail.id)
            for detail in fee:
                fee_due_type.append(detail.due_type)
            return fee_due_type
        except Fee.DoesNotExist:
            return None

    def get_school_fee(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.school_fee
        except Fee.DoesNotExist:
            return None

    def get_total_due_amount(self, obj):
        try:
            fee_due_amount = []
            fee_detail = Fee.objects.get(name=obj)
            fee = DueFeeDetail.objects.filter(fee_structure=fee_detail.id)
            for detail in fee:
                fee_due_amount.append(detail.due_amount)
            return fee_due_amount
        except Fee.DoesNotExist:
            return None

    def get_bus_fee(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.bus_fee
        except Fee.DoesNotExist:
            return None

    def get_monthly_instalment(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.instalment_amount
        except Fee.DoesNotExist:
            return None

    def get_no_of_instalment(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.no_of_instalment
        except Fee.DoesNotExist:
            return None

    def get_canteen_fee(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.canteen_fee
        except Fee.DoesNotExist:
            return None

    def get_miscellaneous_fee(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.miscellaneous_fee
        except Fee.DoesNotExist:
            return None

    def get_total_fee(self, obj):
        try:
            fee_detail = Fee.objects.get(name=obj)
            return fee_detail.total_fee
        except Fee.DoesNotExist:
            return None


    def get_late_fee(self, obj):
        try:
            late_fee = []
            fee_detail = Fee.objects.get(name=obj)
            fee = DueFeeDetail.objects.filter(fee_structure=fee_detail.id)
            for detail in fee:
                late_fee.append(detail.late_fee)
            return late_fee
        except Fee.DoesNotExist:
            return None


class TeacherListsSerializer(serializers.ModelSerializer):
    mail = serializers.EmailField(source='user.email')
    phone = serializers.SerializerMethodField()
    attendance = serializers.SerializerMethodField()
    class Meta:
        model = TeacherUser
        fields = ['id', 'full_name', 'role', 'mail', 'phone', 'attendance']


    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

    def get_attendance(self, obj):
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        start_date = current_date.replace(day=1)
        end_date = current_date.replace(day=monthrange(current_date.year, current_date.month)[1])

        attendance = TeacherAttendence.objects.filter(teacher=obj, date__range=(start_date, end_date), mark_attendence='P')
        data = []

        if attendance:
            for teacher_attendance in attendance:
                data.append(teacher_attendance.mark_attendence)
            return f'{len(data)}/{monthrange(year, month)[1]}'
        return None


class TeacherFeeDetailSerializer(serializers.ModelSerializer):
    department = serializers.SerializerMethodField()
    institute_name = serializers.SerializerMethodField()
    pan_no = serializers.SerializerMethodField()
    master_days = serializers.SerializerMethodField()
    total_working_days = serializers.SerializerMethodField()
    leave_days = serializers.SerializerMethodField()
    attendance = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    account_type = serializers.SerializerMethodField()
    bank_name = serializers.SerializerMethodField()
    ifsc_code = serializers.SerializerMethodField()
    account_number = serializers.SerializerMethodField()
    total_salary = serializers.SerializerMethodField()
    professional_tax = serializers.SerializerMethodField()
    basic_salary = serializers.SerializerMethodField()
    hra = serializers.SerializerMethodField()
    tds = serializers.SerializerMethodField()
    other_deduction = serializers.SerializerMethodField()
    other_allowances = serializers.SerializerMethodField()
    in_hand_salary = serializers.SerializerMethodField()
    total_deduction = serializers.SerializerMethodField()
    class Meta:
        model = TeacherUser
        fields = ['id', 'institute_name', 'full_name', 'department', 'joining_date', 'pan_no', 'master_days', 'total_working_days',
                  'leave_days', 'attendance', 'designation', 'account_type', 'bank_name', 'ifsc_code', 'account_number', 'total_salary',
                  'professional_tax', 'basic_salary', 'hra', 'tds', 'other_deduction', 'other_allowances', 'in_hand_salary',
                  'total_deduction']

    def get_institute_name(self, obj):
        teaching_staff = TeacherUser.objects.get(user=obj.user)
        user = User.objects.get(id=teaching_staff.user.id)
        school = SchoolProfile.objects.get(school_id=user.school_id)
        return f"{school.school_name} {school.city} {school.state}"

    def get_department(self, obj):
        department = Salary.objects.get(name=obj.user)
        return department.department

    def get_pan_no(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.pan_no

    def get_master_days(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.master_days

    def get_total_working_days(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.total_working_days

    def get_leave_days(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.leave_days

    def get_attendance(self, obj):
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        start_date = current_date.replace(day=1)
        end_date = current_date.replace(day=monthrange(current_date.year, current_date.month)[1])

        attendance = TeacherAttendence.objects.filter(teacher=obj, date__range=(start_date, end_date), mark_attendence='P')
        data = []

        if attendance:
            for teacher_attendance in attendance:
                data.append(teacher_attendance.mark_attendence)
            return f'{len(data)}/{monthrange(year, month)[1]}'
        return None

    def get_designation(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.designation

    def get_bank_name(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.bank_name

    def get_account_type(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.account_type

    def get_ifsc_code(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.ifsc_code

    def get_account_number(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.account_number

    def get_total_salary(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.total_salary

    def get_professional_tax(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.professional_tax

    def get_basic_salary(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.basic_salary

    def get_hra(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.hra

    def get_tds(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.tds

    def get_other_deduction(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.other_deduction

    def get_other_allowances(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.other_allowances

    def get_incentive(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.incentive

    def get_in_hand_salary(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.in_hand_salary

    def get_total_deduction(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.deducted_salary+teaching_staff.other_deduction



class StaffListsSerializer(serializers.ModelSerializer):
    mail = serializers.EmailField(source='user.email')
    phone = serializers.SerializerMethodField()
    attendance = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    class Meta:
        model = StaffUser
        fields = ['id', 'name', 'role', 'mail', 'phone', 'attendance']


    def get_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'
    def get_phone(self, obj):
        phone_number = obj.user.phone
        if phone_number:
            return str(phone_number)
        return None

    def get_attendance(self, obj):
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        start_date = current_date.replace(day=1)
        end_date = current_date.replace(day=monthrange(current_date.year, current_date.month)[1])

        attendance = StaffAttendence.objects.filter(staff=obj, date__range=(start_date, end_date), mark_attendence='P')
        data = []

        if attendance:
            for staff_attendance in attendance:
                data.append(staff_attendance.mark_attendence)
            return f'{len(data)}/{monthrange(year, month)[1]}'
        return None


class TeacherUserSalaryUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Salary
        fields = ['master_days', 'total_working_days', 'leave_days', 'deducted_salary', 'other_deduction', 'incentive', 'net_payable_amount',
                  'bank_name', 'account_type', 'ifsc_code', 'account_number']


class StaffFeeDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()
    institute_name = serializers.SerializerMethodField()
    pan_no = serializers.SerializerMethodField()
    master_days = serializers.SerializerMethodField()
    total_working_days = serializers.SerializerMethodField()
    leave_days = serializers.SerializerMethodField()
    attendance = serializers.SerializerMethodField()
    designation = serializers.SerializerMethodField()
    account_type = serializers.SerializerMethodField()
    bank_name = serializers.SerializerMethodField()
    ifsc_code = serializers.SerializerMethodField()
    account_number = serializers.SerializerMethodField()
    total_salary = serializers.SerializerMethodField()
    professional_tax = serializers.SerializerMethodField()
    basic_salary = serializers.SerializerMethodField()
    hra = serializers.SerializerMethodField()
    tds = serializers.SerializerMethodField()
    other_deduction = serializers.SerializerMethodField()
    other_allowances = serializers.SerializerMethodField()
    in_hand_salary = serializers.SerializerMethodField()
    total_deduction = serializers.SerializerMethodField()
    class Meta:
        model = StaffUser
        fields = ['id', 'institute_name', 'name', 'department', 'joining_date', 'pan_no', 'master_days', 'total_working_days',
                  'leave_days', 'attendance', 'designation', 'account_type', 'bank_name', 'ifsc_code', 'account_number', 'total_salary',
                  'professional_tax', 'basic_salary', 'hra', 'tds', 'other_deduction', 'other_allowances', 'in_hand_salary',
                  'total_deduction']

    def get_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    def get_institute_name(self, obj):
        teaching_staff = StaffUser.objects.get(user=obj.user)
        user = User.objects.get(id=teaching_staff.user.id)
        school = SchoolProfile.objects.get(school_id=user.school_id)
        return f"{school.school_name} {school.city} {school.state}"

    def get_department(self, obj):
        department = Salary.objects.get(name=obj.user)
        return department.department

    def get_pan_no(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.pan_no

    def get_master_days(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.master_days

    def get_total_working_days(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.total_working_days

    def get_leave_days(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.leave_days

    def get_attendance(self, obj):
        current_date = datetime.now()
        year = current_date.year
        month = current_date.month
        start_date = current_date.replace(day=1)
        end_date = current_date.replace(day=monthrange(current_date.year, current_date.month)[1])

        attendance = StaffAttendence.objects.filter(staff=obj, date__range=(start_date, end_date), mark_attendence='P')
        data = []

        if attendance:
            for teacher_attendance in attendance:
                data.append(teacher_attendance.mark_attendence)
            return f'{len(data)}/{monthrange(year, month)[1]}'
        return None

    def get_designation(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.designation

    def get_bank_name(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.bank_name

    def get_account_type(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.account_type

    def get_ifsc_code(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.ifsc_code

    def get_account_number(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.account_number

    def get_total_salary(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.total_salary

    def get_professional_tax(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.professional_tax

    def get_basic_salary(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.basic_salary

    def get_hra(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.hra

    def get_tds(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.tds

    def get_other_deduction(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.other_deduction

    def get_other_allowances(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.other_allowances

    def get_incentive(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.incentive

    def get_in_hand_salary(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.in_hand_salary

    def get_total_deduction(self, obj):
        teaching_staff = Salary.objects.get(name=obj.user)
        return teaching_staff.deducted_salary+teaching_staff.other_deduction