import calendar
import datetime
import json

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User, Class, AddressDetails, StudentUser
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsStudentUser, IsTeacherUser, IsInSameSchool
from constants import UserLoginMessage, UserResponseMessage, AttendenceMarkedMessage
from curriculum.models import Curriculum
from pagination import CustomPagination
from student.models import StudentAttendence
from student.serializers import StudentUserSignupSerializer, StudentDetailSerializer, StudentListSerializer, \
    studentProfileSerializer, StudentAttendanceSerializer, StudentAttendanceDetailSerializer, \
    StudentAttendanceListSerializer, StudentListBySectionSerializer, StudentAttendanceCreateSerializer
from utils import create_response_data, create_response_list_data, get_student_total_attendance, \
    get_student_total_absent, get_student_attendence_percentage, generate_random_password


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
            image = serializer.validated_data.get('image', '')
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
            religion = serializer.validated_data.get('religion', '')
            blood_group = serializer.validated_data.get('blood_group', '')
            class_enrolled = serializer.validated_data['class_enrolled']
            section = serializer.validated_data['section']
            permanent_address = serializer.validated_data.get('permanent_address', '')
            bus_number = serializer.validated_data.get('bus_number', '')
            bus_route = serializer.validated_data.get('bus_route', '')
            curriculum_data = serializer.validated_data['curriculum']

            try:
                curriculum = Curriculum.objects.get(id=curriculum_data)
                serializer.validated_data['curriculum'] = curriculum
            except Curriculum.DoesNotExist:
                return Response({"message": "Curriculum not found"}, status=status.HTTP_404_NOT_FOUND)

            if user_type == 'student' and serializer.is_valid() == True:
                user = User.objects.create_user(
                    name=name, email=email, user_type=user_type, school_id=request.user.school_id
                )
                password = generate_random_password()
                user.set_password(password)
                user.save()
                user_student = StudentUser.objects.create(
                    user=user, name=name, dob=dob, image=image, father_name=father_name, mother_name=mother_name,
                    gender=gender, father_occupation=father_occupation, religion=religion,
                    admission_date=admission_date,
                    school_fee=school_fee, bus_fee=bus_fee, canteen_fee=canteen_fee, other_fee=other_fee,
                    total_fee=total_fee, blood_group=blood_group, class_enrolled=class_enrolled, father_phone_number=father_phone_number,
                    mother_occupation=mother_occupation, mother_phone_number=mother_phone_number, section=section, permanent_address=permanent_address,
                    bus_number=bus_number, bus_route=bus_route, due_fee=due_fee, curriculum=curriculum
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

        except KeyError as e:
            return Response(f"Missing key in request data: {e}", status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            return Response("User already exist", status=status.HTTP_400_BAD_REQUEST)


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


class StudentListView(APIView):
    """
    This class is created to fetch the list of the student's.
    """
    permission_classes = [IsAdminUser,IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        queryset = StudentUser.objects.filter(user__is_active=True, user__school_id=request.user.school_id)
        if request.query_params:
            name = request.query_params.get('name', None)
            page = request.query_params.get('page_size', None)
            if name:
                queryset = queryset.filter(user__name__icontains=name)

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
                    status=status.HTTP_200_OK,
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


class AttendanceCreateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to create attendance of student's.
    """
    def post(self, request):
        serializer = StudentAttendanceSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = create_response_data(
                status=status.HTTP_201_CREATED,
                message=AttendenceMarkedMessage.ATTENDENCE_MARKED_SUCCESSFULLY,
                data=serializer.data,
            )
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors,
                data=serializer.errors
            )
            return Response(response, status=status.HTTP_200_OK)


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
            data = StudentAttendence.objects.select_related('student').values(
                'student__name',
                'student__class_enrolled',
                'student__section',
                'mark_attendence',
                'date'
            ).order_by('-date')
            # Paginate the queryset
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(data, request)

            serializers = StudentAttendanceListSerializer(result_page, many=True)
            response_data = {
                'status': status.HTTP_200_OK,
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
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response = {
                "message": "An error occurred while fetching attendance list.",
                "error": str(e),
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
                    student_data['date'] = selected_date
                    student_data['mark_attendence'] = None

        response = create_response_data(
            status=status.HTTP_200_OK,
            message="Student list fetched successfully.",
            data=serializer.data
        )
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