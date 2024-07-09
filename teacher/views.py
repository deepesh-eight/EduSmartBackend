import calendar
import datetime
import json

from django.db import IntegrityError
from django.db.models import Q
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import User, Class, TeacherUser, StudentUser, Certificate, TeachersSchedule, \
    TeacherAttendence, StaffUser, Availability
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsTeacherUser, IsInSameSchool
from authentication.serializers import UserLoginSerializer
from authentication.views import NonTeachingStaffDetailView
from constants import UserLoginMessage, UserResponseMessage, ScheduleMessage, AttendenceMarkedMessage, \
    CurriculumMessage, TeacherAvailabilityMessage, ChatMessage, StudyMaterialMessage
from curriculum.models import Curriculum, Subjects
from pagination import CustomPagination
from student.models import ConnectWithTeacher, StudentMaterial
from student.views import FetchStudentDetailView
from teacher.serializers import TeacherUserSignupSerializer, TeacherDetailSerializer, TeacherListSerializer, \
    TeacherProfileSerializer, ScheduleCreateSerializer, ScheduleDetailSerializer, ScheduleListSerializer, \
    ScheduleUpdateSerializer, TeacherAttendanceSerializer, TeacherAttendanceDetailSerializer, \
    TeacherAttendanceListSerializer, SectionListSerializer, SubjectListSerializer, \
    TeacherAttendanceFilterListSerializer, AvailabilityCreateSerializer, \
    ChatRequestMessageSerializer, TeacherChatHistorySerializer, AvailabilityGetSerializer, StudyMaterialListSerializer, \
    StudyMaterialDetailSerializer
from utils import create_response_data, create_response_list_data, generate_random_password,get_teacher_total_attendance, \
    get_teacher_monthly_attendance, get_teacher_total_absent, get_teacher_monthly_absent


# Create your views here.

class TeacherUserCreateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
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
                    name=full_name, email=email, phone=phone, user_type=user_type, school_id=request.user.school_id
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


class FetchTeacherDetailView(APIView):
    """
    This class is created to fetch the detail of the teacher.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            data = TeacherUser.objects.get(id=pk, user__school_id=request.user.school_id)
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
    permission_classes = [IsAdminUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        queryset = TeacherUser.objects.filter(user__is_active=True, user__school_id=request.user.school_id).order_by("-id")
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
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to delete the teacher.
    """

    def delete(self, request, pk):
        try:
            teacher = TeacherUser.objects.get(id=pk, user__school_id=request.user.school_id)
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
    permission_classes = [IsAdminUser, IsInSameSchool]

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
            teacher = TeacherUser.objects.get(id=pk, user__school_id=request.user.school_id)
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


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny, ]
    """
    This class is used to login user.
    """
    def post(self, request):
        try:
            serializer = UserLoginSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            try:
                user = User.objects.get(email=email, is_active=True)
            except User.DoesNotExist:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXISTS,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            if not user.check_password(password):
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.INCORRECT_PASSWORD,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            try:
                refresh = RefreshToken.for_user(user)
            except TokenError as e:
                response = create_response_data(
                    status=status.HTTP_401_UNAUTHORIZED,
                    message= UserResponseMessage.TOKEN_HAS_EXPIRED,
                    data={}
                )
                return Response(response, status=status.HTTP_401_UNAUTHORIZED)
            response_data = create_response_data(
                status=status.HTTP_201_CREATED,
                message=UserLoginMessage.USER_LOGIN_SUCCESSFUL,
                data={
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_type': user.user_type
                }
            )
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValidationError:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class TeacherScheduleCreateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to create schedule for teacher's.
    """
    def post(self, request):
        try:
            serializer = ScheduleCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data.get('end_date', '')
            schedule_data = serializer.validated_data['schedule_data']
            teacher = serializer.validated_data['teacher']

            try:
                teacher = TeacherUser.objects.get(id=teacher, user__school_id=request.user.school_id)
            except TeacherUser.DoesNotExist:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Teacher with id {} does not exist.".format(teacher),
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            schedule_data = TeachersSchedule.objects.create(
                teacher=teacher, start_date=start_date, end_date=end_date, schedule_data=schedule_data, school_id=request.user.school_id)
            response_data = create_response_data(
                    status=status.HTTP_201_CREATED,
                    message=ScheduleMessage.SCHEDULE_CREATED_SUCCESSFULLY,
                    data={},
                )
            return Response(response_data, status=status.HTTP_201_CREATED)
        except KeyError as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as er:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=er.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class TeacherScheduleDetailView(APIView):
    """
    This class is created to fetch the detail of the teacher schedule.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            data = TeachersSchedule.objects.get(id=pk, school_id=request.user.school_id)
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
        except TokenError:
            response = create_response_data(
                status=status.HTTP_401_UNAUTHORIZED,
                message=UserResponseMessage.TOKEN_HAS_EXPIRED,
                data={}
            )
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class TeacherScheduleListView(APIView):
    """
    This class is created to fetch the list of the teacher's schedule.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        queryset = TeachersSchedule.objects.filter(school_id=request.user.school_id).order_by('-id')
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
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to delete the teacher schedule.
    """

    def delete(self, request, pk):
        try:
            schedule_data = TeachersSchedule.objects.get(id=pk, school_id=request.user.school_id)

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
    permission_classes = [IsAdminUser, IsInSameSchool]

    def patch(self, request, pk):
        try:
            teacher_id = int(request.data.get('teacher'))
            teacher = TeacherUser.objects.get(id=teacher_id, user__school_id=request.user.school_id)
            schedule_data_details = request.data.get('schedule_data')
            # schedule_data_str = json.loads(schedule_data_details)
            data = {
                'start_date': request.data.get('start_date'),
                'end_date': request.data.get('end_date'),
                'teacher': teacher.id,
                'schedule_data': schedule_data_details
            }
            staff = TeachersSchedule.objects.get(id=pk, school_id=request.user.school_id)
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
        except TeacherUser.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=ScheduleMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class TeacherScheduleRenewView(APIView):
    """
    This class is used to renew the teacher schedule.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def patch(self, request, pk):
        try:
            data = {
                'start_date': request.data.get('start_date'),
                'end_date': request.data.get('end_date'),
            }
            staff = TeachersSchedule.objects.get(id=pk, school_id=request.user.school_id)
            serializer = ScheduleUpdateSerializer(staff, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=ScheduleMessage.SCHEDULE_renew_SUCCESSFULLY,
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
        except TeacherUser.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=ScheduleMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class TeacherAttendanceCreateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to create attendance of teacher's.
    """
    def post(self, request):
        try:
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
        except ValidationError as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_200_OK)


class FetchAttendanceDetailView(APIView):
    """
    This class is created to fetch the detail of the teacher attendance.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            teacher = TeacherUser.objects.get(id=pk, user__school_id=request.user.school_id)
            data = TeacherAttendence.objects.filter(teacher_id=pk, teacher__user__school_id=request.user.school_id).order_by('-date')

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
                        "class_teacher": f"{teacher.class_subject_section_details[0].get('class')} class" if teacher.role == 'class teacher' else None,
                        "class_section": teacher.class_subject_section_details[0].get('section') if teacher.role == 'class teacher' else None,
                        "subject": teacher.class_subject_section_details[0].get('subject') if teacher.role == 'class teacher' else None,
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
    permission_classes = [IsAdminUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        queryset = TeacherUser.objects.filter(user__is_active=True, user__school_id=request.user.school_id)
        if request.query_params:
            name = request.query_params.get('full_name', None)
            page = request.query_params.get('page_size', None)
            if name:
                queryset = queryset.filter(full_name__icontains=name)

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializers = TeacherAttendanceListSerializer(paginated_queryset, many=True)
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

        serializer = TeacherAttendanceListSerializer(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_200_OK,
            count=len(serializer.data),
            message=UserResponseMessage.USER_LIST_MESSAGE,
            data=serializer.data,
        )
        return Response(response, status=status.HTTP_200_OK)


class SectionListView(APIView):
    """
    This class is used to fetch list of the section.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        try:
            curriculum = request.query_params.get("curriculum")
            classes = request.query_params.get("class_name")
            section_list = StudentUser.objects.filter(user__school_id=request.user.school_id, curriculum=curriculum, class_enrolled=classes)
            serializer = SectionListSerializer(section_list, many=True)
            class_names = [item['section'] for item in serializer.data]
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.SECTION_LIST_MESSAGE,
                data=set(section.upper() for section in class_names)
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class SubjectListView(APIView):
    """
    This class is used to fetch list of the subjects(primary & optional).
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        try:
            curriculum = request.query_params.get("curriculum")
            classes = request.query_params.get("class_name")
            subjects = Curriculum.objects.get(school_id=request.user.school_id, curriculum_name=curriculum, select_class=classes)
            subject = Subjects.objects.filter(curriculum_id=subjects.id)
            serializer = SubjectListSerializer(subject, many=True)
            primary_subject = [item['primary_subject'] for item in serializer.data]
            optional_subject = [item['optional_subject'] for item in serializer.data]
            subject_list = primary_subject + optional_subject
            # flat_subjects = [subject for sublist in subject_list for subject in sublist]
            subjects = [subjects.title() for subjects in subject_list]
            data = {
                "subject": set(subjects)
            }
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.SECTION_LIST_MESSAGE,
                data=data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class TeachersListView(APIView):
    """
    This class is used to fetch list of all the teachers for creating their schedule.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        try:
            teacher_list = TeacherUser.objects.filter(user__is_active=True, user__school_id=request.user.school_id).values('id', 'full_name')
            data = [{"id": teacher['id'], "teacher_name": teacher['full_name']} for teacher in teacher_list]

            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.TEACHER_LIST_MESSAGE,
                data=data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class TeachersCurriculumListView(APIView):
    """
    This class is used to fetch list of curriculum for creating the teacher schedule.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        try:
            teacher_name = request.query_params.get('teacher_name')
            teacher_list = TeacherUser.objects.get(user__is_active=True, user__school_id=request.user.school_id, id=teacher_name)
            # data = {
            #     "curriculum": [teacher['curriculum'] for teacher in teacher_list.class_subject_section_details]
            # }
            curriculum_set = set()
            for teacher in teacher_list.class_subject_section_details:
                curriculum_set.add(teacher['curriculum'])

            distinct_curriculums = list(curriculum_set)

            data = {
                "curriculum": distinct_curriculums
            }
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.CURRICULUM_LIST_MESSAGE,
                data=data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class TeachersClassListView(APIView):
    """
    This class is used to fetch list of class for creating the teacher schedule.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        try:
            teacher_name = request.query_params.get('teacher_name')
            teacher_curriculum = request.query_params.get('curriculum')
            teacher_list = TeacherUser.objects.get(user__is_active=True, user__school_id=request.user.school_id, id=teacher_name)
            class_set = set()
            for teacher in teacher_list.class_subject_section_details:
                if teacher['curriculum'] == teacher_curriculum:
                    class_set.add(teacher['class'])

            distinct_class = list(class_set)

            data = {
                "class": distinct_class
            }
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.CLASSES_LIST_MESSAGE,
                data=data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class TeachersSectionListView(APIView):
    """
    This class is used to fetch list of section's for creating the teacher schedule.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        try:
            teacher_name = request.query_params.get('teacher_name')
            teacher_curriculum = request.query_params.get('curriculum')
            teacher_class = request.query_params.get('class')
            teacher_list = TeacherUser.objects.get(user__is_active=True, user__school_id=request.user.school_id, id=teacher_name)
            section_set = set()
            for teacher in teacher_list.class_subject_section_details:
                if teacher['class'] == teacher_class and teacher['curriculum'] == teacher_curriculum:
                    section_set.add(teacher['section'])

            distinct_sections = list(section_set)

            data = {
                "section": distinct_sections
            }
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.SECTION_LIST_MESSAGE,
                data=data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class TeachersSubjectListView(APIView):
    """
    This class is used to fetch list of subject's for creating the teacher schedule.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        try:
            teacher_name = request.query_params.get('teacher_name')
            teacher_curriculum = request.query_params.get('curriculum')
            teacher_class = request.query_params.get('class')
            teacher_section = request.query_params.get('section')
            teacher_list = TeacherUser.objects.get(user__is_active=True, user__school_id=request.user.school_id, id=teacher_name)
            subject_set = set()
            for teacher in teacher_list.class_subject_section_details:
                if teacher['class'] == teacher_class and teacher['curriculum'] == teacher_curriculum and teacher['section'] == teacher_section:
                    subject_set.add(teacher['subject'])

            distinct_subject = list(subject_set)

            data = {
                "subject": distinct_subject
            }
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.SUBJECT_LIST_MESSAGE,
                data=data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class AttedanceFilterListView(APIView):
    """
    This class is used to add filter in the list of teacher attendance.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            teacher = TeacherUser.objects.filter(user__school_id=request.user.school_id)
            attendance_data = TeacherAttendence.objects.filter(teacher__in=teacher, teacher__user__school_id=request.user.school_id)

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

            serializers = TeacherAttendanceFilterListSerializer(result_page, many=True)
            response = {
                'status': status.HTTP_200_OK,
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
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class AvailabilityCreateView(APIView):
    """
    This class is used to create the availability time of the teacher.
    """
    permission_classes = [IsTeacherUser, IsInSameSchool]

    def post(self, request):
        try:
            user = request.user
            teacher = TeacherUser.objects.get(user=request.user.id, user__school_id=user.school_id)
            availability = Availability.objects.filter(teacher=teacher.id).exists()
            if availability:
                response_data = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=TeacherAvailabilityMessage.TEACHER_AVAILABILITY_ALREADY_CREATED,
                    data={}
                )
                return Response(response_data, status=status.HTTP_201_CREATED)
            serializer = AvailabilityCreateSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(teacher=teacher, school_id=user.school_id)
                response_data = create_response_data(
                    status=status.HTTP_201_CREATED,
                    message=TeacherAvailabilityMessage.TEACHER_AVAILABILITY_CREATED,
                    data=serializer.data
                )
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response_data= create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
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


class AvailabilityUpdateView(APIView):
    """
    This class is used to update the availability time of the teacher.
    """
    permission_classes = [IsTeacherUser, IsInSameSchool]

    def patch(self, request):
        try:
            user = request.user
            teacher = TeacherUser.objects.get(user__school_id=user.school_id, user=user.id)
            availability_data = Availability.objects.get(school_id=user.school_id,teacher=teacher.id)
            serializer = AvailabilityCreateSerializer(availability_data, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                if serializer.is_valid(raise_exception=True):
                    serializer.save(school_id=user.school_id)
                    response_data = create_response_data(
                        status=status.HTTP_201_CREATED,
                        message=TeacherAvailabilityMessage.TEACHER_AVAILABILITY_UPDATED,
                        data=serializer.data
                    )
                    return Response(response_data, status=status.HTTP_201_CREATED)
                else:
                    response_data = create_response_data(
                        status=status.HTTP_400_BAD_REQUEST,
                        message=serializer.errors,
                        data={}
                    )
                    return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Availability.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=TeacherAvailabilityMessage.TEACHER_AVAILABILITY_NOT_EXIST,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class AvailabilityGetView(APIView):
    """
    This class is used to fetch the availability time of the teacher.
    """
    permission_classes = [IsTeacherUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            teacher = TeacherUser.objects.get(user__school_id=user.school_id, user=user.id)
            availability_data = Availability.objects.get(school_id=user.school_id, teacher=teacher.id)
            serializer = AvailabilityGetSerializer(availability_data)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=TeacherAvailabilityMessage.TEACHER_AVAILABILITY_TIME,
                data=serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Availability.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=TeacherAvailabilityMessage.TEACHER_AVAILABILITY_NOT_EXIST,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentChatRequestView(APIView):
    """
    This class is used to fetch the chat request which is sended by student.
    """
    permission_classes = [IsTeacherUser, IsInSameSchool]

    def get(self, request):
        try:
            teacher = TeacherUser.objects.get(user__school_id= request.user.school_id, user=request.user.id)
            chat_data = ConnectWithTeacher.objects.filter(school_id= request.user.school_id, teacher=teacher.id, status__in=[0, 1]).order_by('-id')
            serializer = ChatRequestMessageSerializer(chat_data, many=True)
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


class StudentChatRequestAcceptView(APIView):
    """
    This class is used to accept the chat request which is sended by student.
    """
    permission_classes = [IsTeacherUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            chat_data = ConnectWithTeacher.objects.filter(school_id=request.user.school_id, id=pk)
            accept = request.query_params.get('1', None)
            join = request.query_params.get('2', None)
            cancel = request.query_params.get('3', None)

            if accept is not None:
                chat_data.update(status=1)
            elif join is not None:
                chat_data.update(status=2)
            elif cancel is not None:
                chat_data.update(status=3)

            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ChatMessage.CHAT_REQUEST_ACCEPTED,
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


class StudentChatRequestJoinView(APIView):
    """
    This class is used to join the chat request which is sended by student.
    """
    permission_classes = [IsTeacherUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            chat_data = ConnectWithTeacher.objects.filter(school_id=request.user.school_id, status=1, id=pk)
            chat_data.update(status=2)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ChatMessage.CHAT_JOIN,
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


class StudentChatHistoryView(APIView):
    """
    This class is used to chat history of the teacher.
    """
    permission_classes = [IsTeacherUser, IsInSameSchool]

    def get(self, request):
        try:
            chat_data = ConnectWithTeacher.objects.filter(school_id=request.user.school_id, status=2)
            serializer = TeacherChatHistorySerializer(chat_data, many=True)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ChatMessage.CHAT_HISTORY_FETCH,
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


class StudyMaterialView(APIView):
    """
    This class is used to fetch list of study material.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            data = StudentMaterial.objects.filter(school_id=request.user.school_id).order_by('-id')
            if self.request.query_params:
                search = self.request.query_params.get('search', None)
                if search is not None:
                    data = data.filter(Q(content_type__icontains=search) | Q(subject__icontains=search) | Q(curriculum__icontains=search) | Q
                    (class_name__icontains=search) | Q(section__icontains=search) | Q(title__icontains=search) | Q(discription__icontains=search))


            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(data, request)

            serializer = StudyMaterialListSerializer(paginated_queryset, many=True)
            response_data = {
                'status': status.HTTP_200_OK,
                'count': len(serializer.data),
                'message': StudyMaterialMessage.STUDY_MATERIAL_FETCHED_SUCCESSFULLY,
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
        except TokenError:
            response = create_response_data(
                status=status.HTTP_401_UNAUTHORIZED,
                message=UserResponseMessage.TOKEN_HAS_EXPIRED,
                data={}
            )
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class StudyMaterialInfoView(APIView):
    """
    This class is used to fetch detail of the study material.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            data = StudentMaterial.objects.get(id=pk, school_id=request.user.school_id)
            serializer = StudyMaterialDetailSerializer(data)
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
        except TokenError:
            response = create_response_data(
                status=status.HTTP_401_UNAUTHORIZED,
                message=UserResponseMessage.TOKEN_HAS_EXPIRED,
                data={}
            )
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class StudyMaterialInfoDeleteView(APIView):
    """
    This class is used to delete detail of the study material.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def delete(self, request, pk):
        try:
            data = StudentMaterial.objects.get(id=pk, school_id=request.user.school_id)
            data.delete()
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=StudyMaterialMessage.STUDY_MATERIAL_DELETED_SUCCESSFULLY,
                data={},
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except StudentMaterial.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=StudyMaterialMessage.STUDY_MATERIAL_Not_Exist,
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
        except TokenError:
            response = create_response_data(
                status=status.HTTP_401_UNAUTHORIZED,
                message=UserResponseMessage.TOKEN_HAS_EXPIRED,
                data={}
            )
            return Response(response, status=status.HTTP_401_UNAUTHORIZED)


class TeacherUpdateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    parser_classes = [MultiPartParser, FormParser]

    def patch(self, request, pk):
        try:
            files_data = {}
            for key, value in request.FILES.items():
                if key.startswith('certificate_files_'):
                    index = key.split('_')[-1]
                    files_data[index] = value

            class_subject_section_details = request.data.get('class_subject_section_details')
            class_subject_section_details_str = json.loads(class_subject_section_details)
            # Retrieve the teacher instance
            teacher = TeacherUser.objects.get(id=pk, user__school_id=request.user.school_id)
            data = {
                'email': request.data.get('email'),
                'phone': request.data.get('phone'),
                'full_name': request.data.get('full_name'),
                'dob': request.data.get('dob'),
                'image': request.data.get('image') if 'image' in request.data and request.data.get('image') else str(teacher.image),
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
            }

            # Iterate through certificate files to update or create
            for cert_id, file in files_data.items():
                try:
                    cert_id = int(cert_id)
                    if Certificate.objects.filter(id=cert_id).exists():
                        # Update existing certificate
                        certificate = Certificate.objects.get(id=cert_id)
                        certificate.certificate_file = file
                        certificate.save()
                    else:
                        # Create new certificate
                        Certificate.objects.create(user=teacher.user, certificate_file=file)
                except ValueError:
                    # Handle case where cert_id is not a valid integer
                    raise ValidationError(f"Invalid certificate ID: {cert_id}")

            # Update teacher profile data
            serializer = TeacherProfileSerializer(teacher, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                # Respond with success message
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=UserResponseMessage.PROFILE_UPDATED_SUCCESSFULLY,
                    data={}
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                # Respond with serializer errors
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data=serializer.errors
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except TeacherUser.DoesNotExist:
            # Handle case where teacher user does not exist
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        except IntegrityError as e:
            # Handle case where email already exists (IntegrityError)
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserResponseMessage.EMAIL_ALREADY_EXIST,
                data={},
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except ValidationError as e:
            # Handle validation errors
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)