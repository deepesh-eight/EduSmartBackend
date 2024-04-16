import calendar
import datetime
import json

from django.db import IntegrityError
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import User, Class, TeacherUser, StudentUser, Certificate, TeachersSchedule, \
    TeacherAttendence
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsTeacherUser
from authentication.serializers import UserLoginSerializer
from constants import UserLoginMessage, UserResponseMessage, ScheduleMessage, AttendenceMarkedMessage
from pagination import CustomPagination
from teacher.serializers import TeacherUserSignupSerializer, TeacherDetailSerializer, TeacherListSerializer, \
    TeacherProfileSerializer, ScheduleCreateSerializer, ScheduleDetailSerializer, ScheduleListSerializer, \
    ScheduleUpdateSerializer, TeacherAttendanceSerializer, TeacherAttendanceDetailSerializer, \
    TeacherAttendanceListSerializer
from utils import create_response_data, create_response_list_data, generate_random_password,get_teacher_total_attendance, \
    get_teacher_monthly_attendance, get_teacher_total_absent, get_teacher_monthly_absent


# Create your views here.

class TeacherUserCreateView(APIView):
    permission_classes = [IsAdminUser]
    """
    This class is used to create teacher type user's.
    """

    def post(self, request):
        try:
            serializer = TeacherUserSignupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            full_name = serializer.validated_data['full_name']
            email = serializer.validated_data['email']
            phone = serializer.validated_data['phone']
            user_type = serializer.validated_data['user_type']

            dob = serializer.validated_data['dob']
            image = serializer.validated_data['image']
            gender = serializer.validated_data['gender']
            joining_date = serializer.validated_data['joining_date']
            religion = serializer.validated_data['religion']
            blood_group = serializer.validated_data['blood_group']
            ctc = serializer.validated_data['ctc']

            experience = serializer.validated_data['experience']
            role = serializer.validated_data['role']
            address = serializer.validated_data['address']
            class_subject_section_details = serializer.validated_data['class_subject_section_details']
            highest_qualification = serializer.validated_data['highest_qualification']
            certificates = serializer.validated_data.get('certificate_files', [])


            if user_type == 'teacher' and serializer.is_valid() == True:
                user = User.objects.create_user(
                    name=full_name, email=email, phone=phone, user_type=user_type
                )
                password = generate_random_password()
                user.set_password(password)
                user.save()
                user_teacher = TeacherUser.objects.create(
                    user=user, dob=dob, image=image, gender=gender, joining_date=joining_date, full_name=full_name,
                    religion=religion, blood_group=blood_group, ctc=ctc,
                    experience=experience, role=role, address=address,
                    class_subject_section_details=class_subject_section_details,
                    highest_qualification=highest_qualification,
                )
                for cert_file in certificates:
                    Certificate.objects.create(user=user, certificate_file=cert_file)
            else:
                raise ValidationError("Invalid user_type. Expected 'teacher'.")
            response_data = {
                'user_id': user_teacher.id,
                'name': user.name,
                'email': user.email,
                'phone': str(user.phone),
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


class FetchTeacherDetailView(APIView):
    """
    This class is created to fetch the detail of the teacher.
    """
    permission_classes = [IsAdminUser,]

    def get(self, request, pk):
        try:
            data = TeacherUser.objects.get(id=pk)
            if data.user.is_active == True:
                serializer = TeacherDetailSerializer(data)
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
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class TeacherListView(APIView):
    """
    This class is created to fetch the list of the teacher's.
    """
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination

    def get(self, request):
        queryset = TeacherUser.objects.filter(user__is_active=True)
        if request.query_params:
            name = request.query_params.get('full_name', None)
            page = request.query_params.get('page_size', None)
            if name:
                queryset = queryset.filter(full_name__icontains=name)

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializers = TeacherListSerializer(paginated_queryset, many=True)
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

        serializer = TeacherListSerializer(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_200_OK,
            count=len(serializer.data),
            message=UserResponseMessage.USER_LIST_MESSAGE,
            data=serializer.data,
        )
        return Response(response, status=status.HTTP_200_OK)


class TeacherDeleteView(APIView):
    permission_classes = [IsAdminUser]
    """
    This class is used to delete the teacher.
    """

    def delete(self, request, pk):
        try:
            teacher = TeacherUser.objects.get(id=pk)
            user = User.objects.get(id=teacher.user_id)
            if teacher.user.user_type == "teacher":
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


class TeacherUpdateProfileView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            files_data = []
            certificate_files = request.data.getlist('certificate_files')

            for file in certificate_files:
                files_data.append(file)

            class_subject_section_details = request.data.get('class_subject_section_details')
            class_subject_section_details_str = json.loads(class_subject_section_details)
            data = {
                'email': request.data.get('email'),
                'phone': request.data.get('phone'),
                'full_name': request.data.get('full_name'),
                'dob': request.data.get('dob'),
                'image': request.data.get('image'),
                'gender': request.data.get('gender'),
                'joining_date': request.data.get('joining_date'),
                'religion': request.data.get('religion'),
                'blood_group': request.data.get('blood_group'),
                'ctc': request.data.get('ctc'),
                'experience': request.data.get('experience'),
                'role': request.data.get('role'),
                'address': request.data.get('address'),
                'class_subject_section_details': class_subject_section_details_str,
                'highest_qualification': request.data.get('highest_qualification'),
                'certificate_files': files_data
            }
            teacher = TeacherUser.objects.get(id=pk)
            serializer = TeacherProfileSerializer(teacher, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                # Update certificates separately
                if files_data:
                    teacher.user.certificates.all().delete()  # Delete existing certificates
                    for cert_file_data in files_data:
                        Certificate.objects.create(user=teacher.user, certificate_file=cert_file_data)
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=UserResponseMessage.PROFILE_UPDATED_SUCCESSFULLY,
                    data={}
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=serializer.errors,
                    data=serializer.errors
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except TeacherUser.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except IntegrityError as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserResponseMessage.EMAIL_ALREADY_EXIST,
                data={},
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class TeacherLoginView(APIView):
    permission_classes = [permissions.AllowAny, ]
    """
    This class is used to login teacher user.
    """
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            teacher_user = TeacherUser.objects.get(user__email=email)
            user = User.objects.get(email=email)
        except TeacherUser.DoesNotExist:
            resposne = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(resposne, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.INCORRECT_PASSWORD,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        teacher_detail = FetchTeacherDetailView.get(self, request, teacher_user.id)

        refresh = RefreshToken.for_user(user)
        response_data = create_response_data(
            status=status.HTTP_201_CREATED,
            message=UserLoginMessage.SIGNUP_SUCCESSFUL,
            data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'teacher_data':teacher_detail.data.get('data')
            }
        )
        return Response(response_data, status=status.HTTP_201_CREATED)


class TeacherScheduleCreateView(APIView):
    permission_classes = [IsAdminUser, ]
    """
    This class is used to create schedule for teacher's.
    """
    def post(self, request):
        serializer = ScheduleCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = create_response_data(
                status=status.HTTP_201_CREATED,
                message=ScheduleMessage.SCHEDULE_CREATED_SUCCESSFULLY,
                data={},
            )
            return Response(response_data, status=status.HTTP_201_CREATED)
        else:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors,
                data=serializer.errors
            )
            return Response(response, status=status.HTTP_200_OK)

class TeacherScheduleDetailView(APIView):
    """
    This class is created to fetch the detail of the teacher schedule.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, pk):
        try:
            data = TeachersSchedule.objects.get(id=pk)
            if data:
                serializer = ScheduleDetailSerializer(data)
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=ScheduleMessage.SCHEDULE_FETCHED_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = create_response_data(
                    status=status.HTTP_404_NOT_FOUND,
                    message=ScheduleMessage.SCHEDULE_NOT_FOUND,
                    data={}
                )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=ScheduleMessage.SCHEDULE_NOT_FOUND,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class TeacherScheduleListView(APIView):
    """
    This class is created to fetch the list of the teacher's schedule.
    """
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination

    def get(self, request):
        queryset = TeachersSchedule.objects.all()
        if request.query_params:
            start_date = request.query_params.get('start_date', None)
            end_date = request.query_params.get('end_date', None)

            if start_date and end_date:
                queryset = queryset.filter(start_date__gte=start_date, end_date__lte=end_date)
            elif start_date:
                queryset = queryset.filter(start_date__gte=start_date)
            elif end_date:
                queryset = queryset.filter(end_date__lte=end_date)

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializers = ScheduleListSerializer(paginated_queryset, many=True)
            response_data = {
                'status': status.HTTP_200_OK,
                'count': len(serializers.data),
                'message': ScheduleMessage.SCHEDULE_LIST_MESSAGE,
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

        serializer = ScheduleListSerializer(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_200_OK,
            count=len(serializer.data),
            message=ScheduleMessage.SCHEDULE_LIST_MESSAGE,
            data=serializer.data,
        )
        return Response(response, status=status.HTTP_200_OK)


class TeacherScheduleDeleteView(APIView):
    permission_classes = [IsAdminUser]
    """
    This class is used to delete the teacher schedule.
    """

    def delete(self, request, pk):
        try:
            schedule_data = TeachersSchedule.objects.get(id=pk)

            schedule_data.delete()
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ScheduleMessage.SCHEDULE_DELETED_SUCCESSFULLY,
                data={}
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except TeachersSchedule.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=ScheduleMessage.SCHEDULE_NOT_FOUND,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class TeacherScheduleUpdateView(APIView):
    """
    This class is used to update the teacher schedule.
    """
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            schedule_data_details = request.data.get('schedule_data')
            schedule_data_str = json.loads(schedule_data_details)
            data = {
                'start_date': request.data.get('start_date'),
                'end_date': request.data.get('end_date'),
                'schedule_data':schedule_data_str
            }
            staff = TeachersSchedule.objects.get(id=pk)
            serializer = ScheduleUpdateSerializer(staff, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=ScheduleMessage.SCHEDULE_UPDATED_SUCCESSFULLY,
                    data={}
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=serializer.errors,
                    data=serializer.errors
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except TeachersSchedule.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=ScheduleMessage.SCHEDULE_NOT_FOUND,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class TeacherAttendanceCreateView(APIView):
    permission_classes = [IsAdminUser, ]
    """
    This class is used to create attendance of teacher's.
    """
    def post(self, request):
        serializer = TeacherAttendanceSerializer(data=request.data)
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
    This class is created to fetch the detail of the teacher attendance.
    """
    permission_classes = [IsAdminUser,]

    def get(self, request, pk):
        try:
            teacher = TeacherUser.objects.get(id=pk)
            data = TeacherAttendence.objects.filter(teacher_id=pk).order_by('-date')

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
                serializer = TeacherAttendanceDetailSerializer(data, many=True)
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=UserResponseMessage.USER_DETAIL_MESSAGE,
                    data={
                        "teacher_name": teacher.full_name,
                        "teacher_id": teacher.id,
                        "class_teacher": f"{teacher.class_subject_section_details[0].get('class')} class" if teacher.role == 'class_teacher' else None,
                        "class_section": teacher.class_subject_section_details[0].get('section') if teacher.role == 'class_teacher' else None,
                        "subject": teacher.class_subject_section_details[0].get('subject') if teacher.role == 'class_teacher' else None,
                        "total_attendance": get_teacher_total_attendance(data),
                        "monthly_attendance": get_teacher_monthly_attendance(data),
                        "total_absent": get_teacher_total_absent(data),
                        "monthly_absent": get_teacher_monthly_absent(data),
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
    This class is created to fetch the list of the teacher's attendance.
    """
    permission_classes = [IsAdminUser, ]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            data = TeacherAttendence.objects.select_related('teacher').values(
                'teacher__class_subject_section_details',
                'teacher__role',
                'teacher__full_name',
                'teacher__id',
                'mark_attendence',
                'date'
            ).order_by('-date')

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

            present_staff = request.query_params.get('present_staff', None)
            absent_staff = request.query_params.get('absent_staff', None)
            on_leave = request.query_params.get('on_leave', None)
            if present_staff:
                data = data.filter(mark_attendence='P')
            if absent_staff:
                data = data.filter(mark_attendence='A')
            if on_leave:
                data = data.filter(mark_attendence='L')

            # Paginate the queryset
            paginator = self.pagination_class()
            result_page = paginator.paginate_queryset(data, request)

            serializers = TeacherAttendanceListSerializer(result_page, many=True)
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
