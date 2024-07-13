import calendar
import datetime
import json
from collections import defaultdict

from django.db import IntegrityError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status, generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User, Class, AddressDetails, StudentUser, TeacherUser, TimeTable, ClassEvent, \
    DayReview, TeachersSchedule, Availability
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsStudentUser, IsTeacherUser, IsInSameSchool
from authentication.serializers import ClassEventDetailSerializer
from bus.models import Bus, Route
from constants import UserLoginMessage, UserResponseMessage, AttendenceMarkedMessage, CurriculumMessage, \
    TimeTableMessage, ReportCardMesssage, StudyMaterialMessage, ZoomLinkMessage, ContentMessages, ClassEventMessage, \
    ScheduleMessage, ChatMessage, TeacherAvailabilityMessage
from content.models import Content
from curriculum.models import Curriculum, Subjects
from pagination import CustomPagination
from student.models import StudentAttendence, ExmaReportCard, StudentMaterial, ZoomLink, ConnectWithTeacher
from student.serializers import StudentUserSignupSerializer, StudentDetailSerializer, StudentListSerializer, \
    studentProfileSerializer, StudentAttendanceDetailSerializer, \
    StudentAttendanceListSerializer, StudentListBySectionSerializer, StudentAttendanceCreateSerializer, \
    AdminClassListSerializer, AdminOptionalSubjectListSerializer, StudentAttendanceSerializer, \
    StudentTimeTableListSerializer, StudentReportCardListSerializer, StudentStudyMaterialListSerializer, \
    StudentZoomLinkSerializer, StudentContentListSerializer, StudentClassEventListSerializer, \
    StudentDayReviewDetailSerializer, ConnectWithTeacherSerializer, StudentSubjectListSerializer, ChatHistorySerializer, \
    StudentUserAttendanceListSerializer
from teacher.serializers import StudentChatRequestMessageSerializer
from utils import create_response_data, create_response_list_data, get_student_total_attendance, \
    get_student_total_absent, get_student_attendence_percentage, generate_random_password
from pytz import timezone as pytz_timezone

class StudentUserCreateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to create student type user's.
    """

    def post(self, request):
        try:
            serializer = StudentUserSignupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            name = serializer.validated_data['name']
            email = serializer.validated_data.get('email', '')
            user_type = serializer.validated_data.get('user_type', '')

            dob = serializer.validated_data['dob']
            image = serializer.validated_data['image']
            father_name = serializer.validated_data.get('father_name', '')
            father_phone_number = serializer.validated_data.get('father_phone_number', '')
            mother_name = serializer.validated_data.get('mother_name', '')
            mother_occupation = serializer.validated_data.get('mother_occupation', '')
            mother_phone_number = serializer.validated_data.get('mother_phone_number', '')
            gender = serializer.validated_data['gender']
            father_occupation = serializer.validated_data.get('father_occupation', '')
            admission_date = serializer.validated_data['admission_date']
            school_fee = serializer.validated_data.get('school_fee', '')
            bus_fee = serializer.validated_data.get('bus_fee', '')
            canteen_fee = serializer.validated_data.get('canteen_fee', '')
            other_fee = serializer.validated_data.get('other_fee', '')
            due_fee = serializer.validated_data.get('due_fee', '')
            total_fee = serializer.validated_data.get('total_fee', '')
            religion = serializer.validated_data['religion']
            blood_group = serializer.validated_data.get('blood_group', '')
            class_enrolled = serializer.validated_data['class_enrolled']
            section = serializer.validated_data['section']
            permanent_address = serializer.validated_data.get('permanent_address', '')
            bus_number = serializer.validated_data.get('bus_number', None)
            bus_route = serializer.validated_data.get('bus_route', None)
            curriculum_data = serializer.validated_data['curriculum']
            enrollment_no = serializer.validated_data.get('enrollment_no', '')
            roll_no = serializer.validated_data.get('roll_no', '')
            guardian_no = serializer.validated_data.get('guardian_no', '')
            optional_subject = serializer.validated_data.get('optional_subject', '')
            current_address = serializer.validated_data.get('current_address', '')

            # try:
            #     curriculum = Curriculum.objects.get(id=curriculum_data)
            #     serializer.validated_data['curriculum'] = curriculum
            # except Curriculum.DoesNotExist:
            #     return Response({"message": "Curriculum not found"}, status=status.HTTP_404_NOT_FOUND)

            if user_type == 'student' and serializer.is_valid() == True:
                user = User.objects.create_user(
                    name=name, email=email, user_type=user_type, school_id=request.user.school_id
                )
                password = generate_random_password()
                user.set_password(password)
                user.save()
                bus= None
                route= None
                if bus_number and bus_route is not None:
                    bus = Bus.objects.get(school_id=request.user.school_id, id=bus_number)
                    route = Route.objects.get(school_id=request.user.school_id, id=bus_route)
                user_student = StudentUser.objects.create(
                    user=user, name=name, dob=dob, image=image, father_name=father_name, mother_name=mother_name,
                    gender=gender, father_occupation=father_occupation, religion=religion,
                    admission_date=admission_date,
                    school_fee=school_fee, bus_fee=bus_fee, canteen_fee=canteen_fee, other_fee=other_fee,
                    total_fee=total_fee, blood_group=blood_group, class_enrolled=class_enrolled, father_phone_number=father_phone_number,
                    mother_occupation=mother_occupation, mother_phone_number=mother_phone_number, section=section, permanent_address=permanent_address,
                    bus_number=bus, bus_route=route, due_fee=due_fee, curriculum=curriculum_data, enrollment_no=enrollment_no, roll_no=roll_no,
                    guardian_no=guardian_no, optional_subject=optional_subject, current_address=current_address
                )
            else:
                raise ValidationError("Invalid user_type. Expected 'student'.")
            response_data = {
                'user_id': user_student.id,
                'name': user_student.name,
                'email': user.email,
                'user_type': user.user_type,
                'password': password
            }
            response = create_response_data(
                status=status.HTTP_201_CREATED,
                message=UserLoginMessage.SIGNUP_SUCCESSFUL,
                data=response_data
            )
            return Response(response, status=status.HTTP_201_CREATED)

        except ValidationError:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors,
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except IntegrityError as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserResponseMessage.EMAIL_ALREADY_EXIST,
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class FetchStudentDetailView(APIView):
    """
    This class is created to fetch the detail of the student.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            data = StudentUser.objects.get(id=pk, user__school_id=request.user.school_id)
            if data.user.is_active == True:
                serializer = StudentDetailSerializer(data)
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=UserResponseMessage.USER_DETAIL_MESSAGE,
                    data=serializer.data
                )
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = create_response_data(
                    status=status.HTTP_404_NOT_FOUND,
                    message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                    data={}
                )
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except StudentUser.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=str(e.args[0]),
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class StudentListView(APIView):
    """
    This class is created to fetch the list of the student's.
    """
    permission_classes = [IsAdminUser,IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        queryset = StudentUser.objects.filter(user__is_active=True, user__school_id=request.user.school_id).order_by("-id")
        if request.query_params:
            name = request.query_params.get('name', None)
            page = request.query_params.get('page_size', None)
            search = self.request.query_params.get('search', None)
            if name:
                queryset = queryset.filter(user__name__icontains=name)
            if search is not None:
                queryset = queryset.filter(Q(curriculum__icontains=search) | Q(class_enrolled__icontains=search) | Q(section__icontains=search) | Q(name__icontains=search))

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializers = StudentListSerializer(paginated_queryset, many=True)
            response_data = {
                'status': status.HTTP_201_CREATED,
                'count': len(serializers.data),
                'message': UserResponseMessage.USER_LIST_MESSAGE,
                'data': serializers.data,
                'pagination': {
                    'page_size': paginator.page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': paginator.page.number,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        serializer = StudentListSerializer(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_200_OK,
            count=len(serializer.data),
            message=UserResponseMessage.USER_LIST_MESSAGE,
            data=serializer.data,
        )
        return Response(response, status=status.HTTP_200_OK)


class StudentDeleteView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to delete the student.
    """

    def delete(self, request, pk):
        try:
            student = StudentUser.objects.get(id=pk, user__school_id=request.user.school_id)
            user = User.objects.get(id=student.user_id)
            if student.user.user_type == "student":
                user.is_active = False
                user.save()
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=UserResponseMessage.USER_DELETE_MESSAGE,
                    data={}
                )
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                return Response("Can't delete this user.")
        except StudentUser.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class StudentUpdateProfileView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to update the student profile.
    """

    def patch(self, request, pk):
        try:
            student = StudentUser.objects.get(id=pk, user__school_id=request.user.school_id)
            serializer = studentProfileSerializer(student, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=UserResponseMessage.PROFILE_UPDATED_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data=serializer.errors
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except StudentUser.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class ClassStudentListView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to create attendance of student's.
    """
    def get(self, request):
        try:
            current_date = timezone.now().date()
            # Fetch distinct class names from the curriculum
            curriculum_data = Curriculum.objects.filter(school_id=request.user.school_id).values('select_class').distinct()

            # Initialize a defaultdict to store sections for each class
            class_sections = defaultdict(list)
            for curriculum_entry in curriculum_data:
                class_name = curriculum_entry['select_class']
                # Fetch sections associated with each class from StudentUser
                sections = StudentUser.objects.filter(class_enrolled=class_name, user__school_id=request.user.school_id).values_list('section', flat=True).distinct()
                class_sections[class_name] = list(sections)

            class_teacher_info = []
            class_student_count = []
            class_attendance_info = []

            # Iterate through each class and its associated sections
            for class_name, sections in class_sections.items():
                for section in sections:
                    # Fetch teacher info for the class and section
                    teacher_info = TeacherUser.objects.filter(class_subject_section_details__0__class=class_name, class_subject_section_details__0__section=section,
                                                              user__school_id=request.user.school_id, user__is_active=True).values('full_name', 'class_subject_section_details__0__curriculum')

                    for teacher in teacher_info:
                        # Append teacher info
                        class_teacher_info.append({
                            'curriculum': teacher['class_subject_section_details__0__curriculum'],
                            'class_name': class_name,
                            'section': section,
                            'teachers': teacher['full_name']
                        })

                    # Count students for the class and section
                    student_count = StudentUser.objects.filter(class_enrolled=class_name, section=section, user__school_id=request.user.school_id).count()
                    class_student_count.append({
                        'class_name': class_name,
                        'section': section,
                        'student_count': student_count
                    })

                    # Calculate attendance for the class and section
                    total_present = StudentAttendence.objects.filter(date=current_date, student__class_enrolled=class_name, student__section=section,
                                                                     mark_attendence='P').count()
                    total_absent = StudentAttendence.objects.filter(date=current_date, student__class_enrolled=class_name, student__section=section,
                                                                    mark_attendence='A').count()
                    class_attendance_info.append({
                        'class_name': class_name,
                        'section': section,
                        'total_present': total_present,
                        'total_absent': total_absent
                    })

            response_data = []
            for teacher_info, student_info, attendance_info in zip(class_teacher_info, class_student_count, class_attendance_info):
                response_data.append({
                    'curriculum': teacher_info['curriculum'],
                    'class_name': teacher_info['class_name'],
                    'section': teacher_info['section'],
                    'class_teacher': teacher_info['teachers'],
                    'class_strength': student_info['student_count'],
                    'total_present': attendance_info['total_present'],
                    'total_absent': attendance_info['total_absent']
                })

            response = {
                "status": status.HTTP_200_OK,
                "message": CurriculumMessage.CURRICULUM_LIST_MESSAGE,
                "date": current_date,
                "data": response_data
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class FetchAttendanceDetailView(APIView):
    """
    This class is created to fetch the detail of the student attendance.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            student = StudentUser.objects.get(id=pk, user__school_id=request.user.school_id)
            data = StudentAttendence.objects.filter(student_id=pk, student__user__school_id=request.user.school_id).order_by('-date')

            filter_type = request.query_params.get('filter_type', None)
            if filter_type:
                today = datetime.date.today()
                if filter_type == 'weekly':
                    start_date = today - datetime.timedelta(days=today.weekday())
                    end_date = start_date + datetime.timedelta(days=6)
                elif filter_type == 'monthly':
                    start_date = today.replace(day=1)
                    end_date = today.replace(day=calendar.monthrange(today.year, today.month)[1])
                elif filter_type == 'yearly':
                    start_date = today.replace(month=1, day=1)
                    end_date = today.replace(month=12, day=31)
                data = data.filter(date__range=(start_date, end_date))

            start_date = request.query_params.get('start_date', None)
            date = request.query_params.get('date', None)
            end_date = request.query_params.get('end_date', None)
            if start_date and end_date:
                start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
                end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
                data = data.filter(date__range=(start_date, end_date))
            if date:
                date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                data = data.filter(date=(date))

            if data:
                serializer = StudentAttendanceDetailSerializer(data, many=True)
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=UserResponseMessage.USER_DETAIL_MESSAGE,
                    data={
                        "student_name": student.name,
                        "student_roll_no": student.id,
                        "class": student.class_enrolled,
                        "section": student.section,
                        "total_attendance": get_student_total_attendance(data),
                        "total_absent": get_student_total_absent(data),
                        "total_percentage": f"{get_student_attendence_percentage(data)}%",
                        "attendence_detail": serializer.data,
                    }
                )
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = create_response_data(
                    status=status.HTTP_404_NOT_FOUND,
                    message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                    data={}
                )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class FetchAttendanceListView(APIView):
    """
    This class is created to fetch the list of the student attendance according to class.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            class_name = request.query_params.get('class_name')
            section = request.query_params.get('section')
            current_date = timezone.now().date()
            students = StudentUser.objects.filter(class_enrolled=class_name, section=section, user__school_id=request.user.school_id)
            attendance_data = StudentAttendence.objects.filter(date=current_date, student__in=students, student__user__school_id=request.user.school_id)

            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(attendance_data, request)

            serializers = StudentAttendanceListSerializer(result_page, many=True)

            response_data = []
            for attendance in serializers.data:
                response_data.append({
                    'student_id': attendance['student'].id,
                    'student_name': attendance['student'].name,
                    'roll_number': attendance['student'].roll_no,
                    'class': attendance['student'].class_enrolled,
                    'section': attendance['student'].section,
                    'marked_attendance': attendance['mark_attendence'],
                    'attendance_percentage': attendance['percentage'],
                    'total_attendance': attendance['total_attendance'],
                })
            response = {
                'status': status.HTTP_200_OK,
                'message': AttendenceMarkedMessage.STUDENT_ATTENDANCE_FETCHED_SUCCESSFULLY,
                'data': response_data,
                'pagination': {
                    'page_size': paginator.page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': paginator.page.number,
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class FetchAttendanceFilterListView(APIView):
    """
    This class is created to fetch the list of the student attendance according to filter value.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            class_name = request.query_params.get('class_name')
            section = request.query_params.get('section')
            students = StudentUser.objects.filter(class_enrolled=class_name, section=section, user__school_id=request.user.school_id)
            attendance_data = StudentAttendence.objects.filter(student__in=students, student__user__school_id=request.user.school_id)

            date = request.query_params.get('date', None)
            mark_attendence = request.query_params.get('mark_attendence', None)
            if date:
                date = datetime.datetime.strptime(date, '%Y-%m-%d').date()
                attendance_data = attendance_data.filter(date=date)
            if mark_attendence == 'A':
                attendance_data = attendance_data.filter(mark_attendence='A')
            if mark_attendence == 'P':
                attendance_data = attendance_data.filter(mark_attendence='P')
            if mark_attendence == 'L':
                attendance_data = attendance_data.filter(mark_attendence='L')

            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(attendance_data, request)

            serializers = StudentAttendanceListSerializer(result_page, many=True)
            response_data = []
            for attendance in serializers.data:
                response_data.append({
                    'student_id': attendance['student'].id,
                    'student_name': attendance['student'].name,
                    'roll_number': attendance['student'].roll_no,
                    'class': attendance['student'].class_enrolled,
                    'section': attendance['student'].section,
                    'marked_attendance': attendance['mark_attendence'],
                    'attendance_percentage': attendance['percentage'],
                    'total_attendance': attendance['total_attendance'],
                })
            response={
                'status': status.HTTP_200_OK,
                'message': AttendenceMarkedMessage.STUDENT_ATTENDANCE_FETCHED_SUCCESSFULLY,
                'data': response_data,
                'pagination': {
                    'page_size': paginator.page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': paginator.page.number,
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class FetchStudentList(APIView):
    """
    This class is created to fetch the list of the student's according to section.
    """
    permission_classes = [IsTeacherUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        class_name = request.query_params.get('class_enrolled')
        section = request.query_params.get('section')
        selected_date_str = request.query_params.get('date')

        if not class_name or not section:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message="Class and section are required.",
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        all_mark = True
        if selected_date_str:
            try:
                selected_date = datetime.datetime.strptime(selected_date_str, '%Y-%m-%d').date()
            except ValueError:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Invalid date format. Please provide date in YYYY-MM-DD format.",
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            selected_date = None

        students = StudentUser.objects.filter(
            class_enrolled=class_name, section=section, user__school_id=request.user.school_id
        )
        serializer = StudentListBySectionSerializer(students, many=True)

        if selected_date:
            attendance_records = StudentAttendence.objects.filter(date=selected_date, student__in=students)
            attendance_mapping = {attendance.student_id: {'date': attendance.date, 'mark_attendence': attendance.mark_attendence} for attendance in attendance_records}

            for student_data in serializer.data:
                student_id = student_data['id']
                if student_id in attendance_mapping:
                    attendance_data = attendance_mapping[student_id]
                    student_data['date'] = attendance_data['date']
                    student_data['mark_attendence'] = attendance_data['mark_attendence']
                else:
                    all_mark = False
                    student_data['date'] = selected_date
                    student_data['mark_attendence'] = None
        response ={
            'status': status.HTTP_200_OK,
            'message': "Student list fetched successfully.",
            'all_attendance_marked': all_mark,
            'data': serializer.data
        }
        return Response(response, status=status.HTTP_200_OK)


class StudentAttendanceCreateView(APIView):
    """
    This class is created to marked_attendance of the student's.
    """
    permission_classes = [IsTeacherUser, IsInSameSchool]

    def post(self, request):
        data_str = request.data.get('data')  # Assuming data is sent as form-data with key 'data'

        try:
            data_json = json.loads(data_str)
        except json.JSONDecodeError:
            return Response("Invalid JSON format", status=status.HTTP_400_BAD_REQUEST)

        for item in data_json:
            serializer = StudentAttendanceCreateSerializer(data=item)
            if serializer.is_valid():
                student_id = item['id']
                date = item['date']
                mark_attendence = item['mark_attendence']
                student_user = get_object_or_404(StudentUser, id=student_id)

                # Create or update attendance record
                StudentAttendence.objects.update_or_create(
                    student=student_user,
                    date=date,
                    mark_attendence=mark_attendence
                )
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response = create_response_data(
            status=status.HTTP_200_OK,
            message=AttendenceMarkedMessage.ATTENDENCE_MARKED_SUCCESSFULLY,
            data={}
        )
        return Response(response, status=status.HTTP_200_OK)


class AdminCurriculumList(APIView):
    """
    This class is used to fetch the list of the curriculum which is added by admin.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        try:
            data = Curriculum.objects.filter(school_id=request.user.school_id).values_list('curriculum_name', flat=True).distinct()
            curriculum = list(data)
            curriculum_list = {
                "curriculum_name": curriculum
            }
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.CURRICULUM_LIST_MESSAGE,
                data=curriculum_list
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class AdminClassesList(APIView):
    """
    This class is used to fetch the list of the classes which is added by admin.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        try:
            curriculum = request.query_params.get("curriculum_name")
            data = Curriculum.objects.filter(curriculum_name=curriculum, school_id=request.user.school_id)
            serializer = AdminClassListSerializer(data, many=True)
            class_names = [item['select_class'] for item in serializer.data]
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.CLASSES_LIST_MESSAGE,
                data=class_names
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class AdminOptionalSubjectList(APIView):
    """
    This class is used to fetch the list of the optional subject which is added by admin according to curriculum.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        try:
            curriculum = request.query_params.get("curriculum_name")
            classes = request.query_params.get("class_name")
            data = Curriculum.objects.get(curriculum_name=curriculum, select_class=classes, school_id=request.user.school_id)
            subject = Subjects.objects.filter(curriculum_id=data.id)
            serializer = AdminOptionalSubjectListSerializer(subject, many=True)
            optional_subj = [item['optional_subject'].title() for item in serializer.data]
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.SUBJECT_LIST_MESSAGE,
                data=set(optional_subj)
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
class StudentAttendanceView(generics.ListAPIView):
    serializer_class = StudentAttendanceSerializer
    permission_classes = [IsStudentUser]

    def get_queryset(self):
        student_user = self.request.user.studentuser
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')

        queryset = StudentAttendence.objects.filter(student=student_user)
        if year and month:
            queryset = queryset.filter(date__year=year, date__month=month)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        response_data = {
            "status": status.HTTP_200_OK,
            "message": AttendenceMarkedMessage.STUDENT_ATTENDANCE_FETCHED_SUCCESSFULLY,
            "data": serializer.data
        }

        return Response(response_data, status=status.HTTP_200_OK)


class StudentTimeTableListView(APIView):
    """
    This class is used to fetch the list of the timetable which is uploaded by teacher.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            student_data = StudentUser.objects.get(user__school_id=user.school_id, user__id=user.id)
            time_table = TimeTable.objects.filter(school_id=user.school_id, curriculum=student_data.curriculum, class_name=student_data.class_enrolled, class_section=student_data.section, status=1)
            serializer = StudentTimeTableListSerializer(time_table, many=True)
            response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=TimeTableMessage.TIMETABLE_FETCHED_SUCCESSFULLY,
                    data=serializer.data
                )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data=create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentReportCardListView(APIView):
    """
    This class is used to fetch the report card of the student.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            student_data = StudentUser.objects.get(user__school_id=user.school_id, user__id=user.id)
            report_card = ExmaReportCard.objects.filter(school_id=user.school_id, curriculum=student_data.curriculum,
                                                  class_name=student_data.class_enrolled,
                                                  class_section=student_data.section, status=1).last()
            serializer = StudentReportCardListSerializer(report_card)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ReportCardMesssage.REPORT_CARD_FETCHED_SUCCESSFULLY,
                data=serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentReportCardFilterListView(APIView):
    """
    This class is used to fetch the report card of the student according to filter values.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            curriculum = request.query_params.get('curriculum', None)
            select_class = request.query_params.get('select_class', None)
            select_section = request.query_params.get('select_section', None)
            select_exam = request.query_params.get('select_exam')
            select_month = datetime.datetime.strptime(request.query_params.get('select_month'), "%Y-%m-%d").strftime("%Y-%m")
            # student_data = StudentUser.objects.get(user__school_id=user.school_id, user__id=user.id)
            report_card = ExmaReportCard.objects.get(school_id=user.school_id, curriculum=curriculum,
                                                  class_name=select_class,
                                                  class_section=select_section, status=1, exam_type=select_exam, exam_month__startswith=select_month)
            serializer = StudentReportCardListSerializer(report_card)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ReportCardMesssage.REPORT_CARD_FETCHED_SUCCESSFULLY,
                data=serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentStudyMaterialListView(APIView):
    """
    This class is used to fetch list of study material.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            student_data = StudentUser.objects.get(user__school_id=user.school_id, user__id=user.id)
            data = StudentMaterial.objects.filter(school_id=user.school_id, curriculum=student_data.curriculum,
                                                  class_name=student_data.class_enrolled,
                                                  section=student_data.section)
            if self.request.query_params:
                search = self.request.query_params.get('search', None)
                if search is not None:
                    data = data.filter(Q(content_type__icontains=search) | Q(subject__icontains=search) | Q(curriculum__icontains=search) | Q
                    (class_name__icontains=search) | Q(subject__icontains=search) | Q(section__icontains=search) | Q(title__icontains=search) | Q(discription__icontains=search))

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(data, request)

            serializer = StudentStudyMaterialListSerializer(paginated_queryset, many=True)
            response_data = {
                'status': status.HTTP_200_OK,
                'count': len(serializer.data),
                'message': UserResponseMessage.USER_LIST_MESSAGE,
                'data': serializer.data,
                'pagination': {
                    'page_size': paginator.page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': paginator.page.number,
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentStudyMaterialDetailView(APIView):
    """
    This class is used to fetch detail of the study material.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            user = request.user
            student_data = StudentUser.objects.get(user__school_id=user.school_id, user__id=user.id)
            data = StudentMaterial.objects.get(id=pk,school_id=user.school_id, curriculum=student_data.curriculum,
                                                  class_name=student_data.class_enrolled,
                                                  section=student_data.section)
            serializer = StudentStudyMaterialListSerializer(data)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=StudyMaterialMessage.STUDY_MATERIAL_FETCHED_SUCCESSFULLY,
                data=serializer.data,
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except StudentMaterial.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=StudyMaterialMessage.STUDY_MATERIAL_Not_Exist,
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentZoomLinkListView(APIView):
    """
    This class is used to fetch list of the zoom link
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            student_data = StudentUser.objects.get(user__school_id=user.school_id, user__id=user.id)

            current_date_time_ist = timezone.localtime(timezone.now(), pytz_timezone('Asia/Kolkata'))

            current_date = current_date_time_ist.date()
            currunt_time_str = current_date_time_ist.time()
            zoom_link_data = ZoomLink.objects.filter(school_id=user.school_id, curriculum=student_data.curriculum, class_name=student_data.class_enrolled,
                                                     section=student_data.section, date__gte=current_date, end_time__gt=currunt_time_str).order_by("date")
            serializer = StudentZoomLinkSerializer(zoom_link_data, many=True)
            response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=ZoomLinkMessage.ZOOM_LINK_FETCHED_SUCCESSFULLY,
                    data=serializer.data,
                )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentEBookListView(APIView):
    """
    This class is used to fetch the list of the content.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            content_data = Content.objects.filter(Q(school_id=self.request.user.school_id) | Q(school_id__isnull=True)).order_by('-id')
            if self.request.query_params:
                content_type = self.request.query_params.get('content_type', None)
                is_recommended = self.request.query_params.get('is_recommended', None)
                search = self.request.query_params.get('search', None)
                if search is not None:
                    content_data = content_data.filter(Q(content_type__icontains=search) | Q(content_name__icontains=search) | Q(curriculum__icontains=search) | Q
                    (classes__icontains=search) | Q(subject__icontains=search) | Q(supporting_detail__icontains=search) | Q(description__icontains=search) | Q(category__icontains=search) | Q(content_creator__icontains=search))
                if content_type is not None:
                    content_data = content_data.filter(content_type=content_type)
                if is_recommended is not None:
                    content_data = content_data.filter(is_recommended=is_recommended, school_id=self.request.user.school_id)

                paginator = self.pagination_class()
                paginated_queryset = paginator.paginate_queryset(content_data, request)
                serializer = StudentContentListSerializer(paginated_queryset, many=True)
                response_data = {
                    'status': status.HTTP_200_OK,
                    'count': len(serializer.data),
                    'message': ContentMessages.CONTENT_FETCHED,
                    'data': serializer.data,
                    'pagination': {
                        'page_size': paginator.page_size,
                        'next': paginator.get_next_link(),
                        'previous': paginator.get_previous_link(),
                        'total_pages': paginator.page.paginator.num_pages,
                        'current_page': paginator.page.number,
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                serializer = StudentContentListSerializer(content_data, many=True)
                response_data = create_response_list_data(
                        status=status.HTTP_200_OK,
                        count=len(serializer.data),
                        message=ContentMessages.CONTENT_FETCHED,
                        data=serializer.data
                    )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentEBookDetailView(APIView):
    """
    This class is used to fetch the detail of the contetent.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            data = Content.objects.get(Q(school_id=self.request.user.school_id) | Q(school_id__isnull=True), id=pk)
            serializer = StudentContentListSerializer(data)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ContentMessages.CONTENT_FETCHED,
                data=serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Content.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=ContentMessages.CONTENT_NOT_EXIST,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentClassEventListView(APIView):
    """
    This class is used to fetch list of the class event which is added by teacher.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            current_date_time_ist = timezone.localtime(timezone.now(), pytz_timezone('Asia/Kolkata'))
            current_date = current_date_time_ist.date()
            student_user = StudentUser.objects.get(user__school_id=user.school_id, user=request.user.id)
            content_data = ClassEvent.objects.filter(school_id=request.user.school_id,curriculum=student_user.curriculum,select_class=student_user.class_enrolled,
                                                     section=student_user.section, date__gte=current_date).order_by('-id')
            date = request.query_params.get('date', None)
            if date is not None:
                content_data = content_data.filter(date=date)
            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(content_data, request)

            serializer = StudentClassEventListSerializer(paginated_queryset, many=True)
            response_data = {
                'status': status.HTTP_200_OK,
                'message': ClassEventMessage.CLASS_EVENT_LIST,
                'count': len(serializer.data),
                'data': serializer.data,
                'pagination': {
                    'page_size': paginator.page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': paginator.page.number,
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentClassEventDetailView(APIView):
    """
    This class is used to fetch the detail of the class event which is added by teacher.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            class_event = ClassEvent.objects.get(school_id=request.user.school_id, id=pk)
            serializer = ClassEventDetailSerializer(class_event)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ClassEventMessage.CLASS_EVENT_LIST,
                data=serializer.data,
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except ClassEvent.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=ClassEventMessage.CLASS_EVENT_NOT_EXIST,
                data={},
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentDayReview(APIView):
    """
    This class is used to fetch the list of the day & review list.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        user = request.user
        current_date_time_ist = timezone.localtime(timezone.now(), pytz_timezone('Asia/Kolkata'))
        current_date_str = current_date_time_ist.date()
        yesterday_date = current_date_time_ist - datetime.timedelta(days=1)

        student_user = StudentUser.objects.get(user__school_id=user.school_id, user=user.id)
        queryset = DayReview.objects.filter(school_id=request.user.school_id,curriculum=student_user.curriculum,class_name=student_user.class_enrolled,
                                                     section=student_user.section, updated_at__date=current_date_str)
        if request.query_params:
            updated_at = request.query_params.get('updated_at', None)
            yesterday = request.query_params.get('yesterday', None)
            if yesterday is not None:
                queryset = DayReview.objects.filter(school_id=request.user.school_id, curriculum=student_user.curriculum, class_name=student_user.class_enrolled,
                                                     section=student_user.section, updated_at__date=yesterday_date.date())
            if updated_at:
                queryset = DayReview.objects.filter(school_id=request.user.school_id, curriculum=student_user.curriculum, class_name=student_user.class_enrolled,
                                                     section=student_user.section, updated_at__date=updated_at)

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializers = StudentDayReviewDetailSerializer(paginated_queryset, many=True)
            response_data = {
                'status': status.HTTP_200_OK,
                'count': len(serializers.data),
                'message': ScheduleMessage.SCHEDULE_LIST_MESSAGE,
                'data': serializers.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        serializer = StudentDayReviewDetailSerializer(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_200_OK,
            count=len(serializer.data),
            message=ScheduleMessage.SCHEDULE_LIST_MESSAGE,
            data=serializer.data,
        )
        return Response(response, status=status.HTTP_200_OK)


class StudentSubjectListView(APIView):
    """
    This class is used to fetch the list of the subject of the student.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            data = StudentUser.objects.get(user=user.id, user__school_id=user.school_id)
            serializer = StudentSubjectListSerializer(data)
            primary_subject = serializer.data.get('subject', [])
            optional_subject = serializer.data.get('optional_subject', [])
            primary_subjects = [subj for subj in primary_subject if subj]
            if isinstance(optional_subject, str):
                optional_subject = [subj.strip() for subj in optional_subject.split(',')]

            subject_list = primary_subjects + optional_subject
            data = {
                "id": serializer.data.get('id'),
                "subject": subject_list,
            }

            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.SUBJECT_LIST_MESSAGE,
                data=data,
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class AvailabilityTimeListView(APIView):
    """
    This class is used to fetch the list of the availability time of the teacher.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request):
        try:
            user= request.user
            current_date_time_ist = timezone.localtime(timezone.now(), pytz_timezone('Asia/Kolkata'))
            current_date = current_date_time_ist.date()
            subject = request.query_params.get('subject')
            student_data = StudentUser.objects.get(user__school_id=user.school_id, user=user.id)
            teacher_schedule = TeachersSchedule.objects.filter(school_id=user.school_id, end_date__gte=str(current_date))
            availability_times = []

            for schedule in teacher_schedule:
                for entry in schedule.schedule_data:
                    if entry['curriculum'] == student_data.curriculum \
                            and entry['class'] == student_data.class_enrolled \
                            and entry['section'] == student_data.section \
                            and entry['subject'] == subject:
                        availability_time_data = Availability.objects.get(school_id=user.school_id, teacher=schedule.teacher.id)

                        # for availability_time in availability_time_data:
                        start_time = datetime.datetime.strptime(str(availability_time_data.start_time), '%H:%M:%S').strftime('%I:%M %p')
                        end_time = datetime.datetime.strptime(str(availability_time_data.end_time), '%H:%M:%S').strftime('%I:%M %p')
                        # availability_times.append({"start_time": start_time, "end_time": end_time})
                        response_data = create_response_data(
                            status=status.HTTP_200_OK,
                            message=TeacherAvailabilityMessage.TEACHER_AVAILABILITY_TIME,
                            data={"start_time": start_time, "end_time": end_time},
                        )
                        return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = create_response_data(
                    status=status.HTTP_404_NOT_FOUND,
                    message="No availability times found for the given criteria",
                    data={},
                )
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class ConnectWithTeacherView(APIView):
    """
    This class is used to connect student with teacher for chat.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def post(self, request):
        try:
            user = request.user
            student_data = StudentUser.objects.get(user__school_id=user.school_id, user=user.id)
            serializer = ConnectWithTeacherSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            subject = serializer.validated_data['subject']
            start_time = serializer.validated_data.get('start_time')
            # end_time = serializer.validated_data.get('end_time')

            teacher_schedules = TeachersSchedule.objects.all()

            for schedule in teacher_schedules:
                for entry in schedule.schedule_data:
                    if entry['curriculum'] == student_data.curriculum \
                            and entry['class'] == student_data.class_enrolled \
                            and entry['section'] == student_data.section \
                            and entry['subject'] == subject:
                        teacher_id = schedule.teacher_id
                        break
                else:
                    continue
                break
            else:
                response = create_response_data(
                    status=status.HTTP_404_NOT_FOUND,
                    message="No teacher available for the provided schedule",
                    data={}
                )
                return Response(response, status=status.HTTP_404_NOT_FOUND)
            teacher = TeacherUser.objects.get(id=teacher_id)
            student = StudentUser.objects.get(user=user.id)
            chat_data_exist = ConnectWithTeacher.objects.filter(Q(start_time=str(start_time)) | Q(end_time=str(start_time)),school_id=user.school_id, teacher=teacher,
                                                                curriculum=student_data.curriculum,
                                                                class_name=student_data.class_enrolled,
                                                                section=student_data.section,
                                                                ).exists()
            if chat_data_exist:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=ChatMessage.CHAT_REQUEST_ALREADY_CREATED,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            else:
                chat_data = ConnectWithTeacher.objects.create(school_id=user.school_id, teacher=teacher, curriculum=student_data.curriculum, class_name=student_data.class_enrolled, section=student_data.section,
                                                              subject=subject, start_time=str(start_time), student=student)

                response = create_response_data(
                    status=status.HTTP_201_CREATED,
                    message=ChatMessage.CHAT_REQUEST_CREATED,
                    data={}
                )
                return Response(response, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class ChatHistoryView(APIView):
    """
    This class is used to fetch history of the chat.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request):
        try:
            chat_data = ConnectWithTeacher.objects.filter(school_id=request.user.school_id)
            serializer = ChatHistorySerializer(chat_data, many=True)
            response = create_response_data(
                status=status.HTTP_200_OK,
                message=ChatMessage.CHAT_HISTORY_FETCH,
                data=serializer.data
            )
            return Response(response, status=status.HTTP_200_OK)

        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class FetchStudentAttendanceView(APIView):
    """
    This class is used to fetch attendance list of student according to provided month
    """
    permission_classes = [IsStudentUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            student = StudentUser.objects.get(user=user.id)
            month = request.query_params.get('month', None)

            if month:
                month = int(month)
                current_year = datetime.date.today().year

                _, last_day = calendar.monthrange(current_year, month)
                start_date = datetime.date(current_year, month, 1)
                end_date = datetime.date(current_year, month, last_day)
                all_days = [start_date + datetime.timedelta(days=day) for day in
                            range((end_date - start_date).days + 1)]

                attendance_records = StudentAttendence.objects.filter(student_id=student.id,
                                                                      date__range=[start_date, end_date],
                                                                      student__user__school_id=request.user.school_id)

                attendance_dict = {record.date: record for record in attendance_records}

                attendance_record = []
                for day in all_days:
                    if day in attendance_dict:
                        attendance = attendance_dict[day]
                        attendance_record.append({
                            "date": day,
                            "day": day.strftime("%A"),
                            "mark_attendence": StudentUserAttendanceListSerializer(attendance).data.get('mark_attendence')
                        })
                    else:
                        # Attendance not marked for this day
                        attendance_record.append({
                            "date": day,
                            "day": day.strftime("%A"),
                            "mark_attendence": None
                        })
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=AttendenceMarkedMessage.ATTENDANCE_FETCHED_SUCCESSFULLY,
                    data=attendance_record,
                )
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Please provide month.",
                    data={},
                )
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentScheduleView(APIView):
    """
    This class is used to fetch list of the student classes schedule.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request):
        try:
            current_date_time_ist = timezone.localtime(timezone.now(), pytz_timezone('Asia/Kolkata'))
            current_date = current_date_time_ist.date()

            student = StudentUser.objects.get(user__school_id=request.user.school_id, user=request.user.id)
            curriculum = Curriculum.objects.get(curriculum_name=student.curriculum, select_class=student.class_enrolled)
            subject_data = Subjects.objects.filter(curriculum_id=curriculum.id)
            subjects = []
            for subject in subject_data:
                subjects.append(subject.primary_subject)

            schedule = TeachersSchedule.objects.filter(school_id=request.user.school_id, start_date__lte=current_date,
                                                       end_date__gte=current_date,)
            matching_schedules = []
            for schedule in schedule:
                for entry in schedule.schedule_data:
                    if (
                            entry.get('curriculum') == student.curriculum and
                            entry.get('class') == student.class_enrolled and
                            (entry.get('subject') in subjects or
                            entry.get('subject') in student.optional_subject) and
                            current_date.strftime("%a") in entry.get('select_days', [])
                    ):
                        matching_schedules.append({
                            "teacher": schedule.teacher.full_name,
                            "schedule_id": schedule.id,
                            "class": entry.get('class'),
                            "section": entry.get('section'),
                            "subject": entry.get('subject'),
                            "curriculum": entry.get('curriculum'),
                            "day": current_date.strftime("%a"),
                            "class_timing": entry.get('class_timing'),
                            "lecture_type": entry.get('lecture_type'),
                            "class_duration": entry.get('class_duration')
                        })
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ScheduleMessage.SCHEDULE_FETCHED_SUCCESSFULLY,
                data=matching_schedules,
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class ChatRequestView(APIView):
    """
    This class is used to get request from the teacher for join meeting
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request):
        try:
            student = StudentUser.objects.get(user__school_id= request.user.school_id, user=request.user.id)
            chat_data = ConnectWithTeacher.objects.filter(school_id= request.user.school_id, student=student.id, status__in=[1]).order_by('-id')
            serializer = StudentChatRequestMessageSerializer(chat_data, many=True)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ChatMessage.CHAT_REQUEST_GET,
                data=serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class JoinChatRequestView(APIView):
    """
    This class is used to join chat which is accepted by teacher.
    """
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            chat_data = ConnectWithTeacher.objects.filter(school_id=request.user.school_id, id=pk)
            join = request.query_params.get('2', None)
            cancel = request.query_params.get('3', None)

            if join is not None:
                chat_data.update(status=2)
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=ChatMessage.CHAT_JOIN,
                    data={}
                )
                return Response(response_data, status=status.HTTP_200_OK)
            elif cancel is not None:
                chat_data.update(status=3)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ChatMessage.CHAT_REQUEST_CANCEL,
                data={}
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)