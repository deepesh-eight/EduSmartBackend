import calendar
import datetime

from django.db import IntegrityError
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import User, AddressDetails, ErrorLogging, Certificate, StaffUser, StaffAttendence, \
    TeacherUser, StudentUser, TeachersSchedule, DayReview
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsManagementUser, IsPayRollManagementUser, \
    IsBoardingUser, IsInSameSchool, IsTeacherUser
from authentication.serializers import UserSignupSerializer, UsersListSerializer, UpdateProfileSerializer, \
    UserLoginSerializer, NonTeachingStaffSerializers, NonTeachingStaffListSerializers, \
    NonTeachingStaffDetailSerializers, NonTeachingStaffProfileSerializers, StaffAttendanceSerializer, \
    StaffAttendanceDetailSerializer, StaffAttendanceListSerializer, LogoutSerializer
from constants import UserLoginMessage, UserResponseMessage, AttendenceMarkedMessage, ScheduleMessage, \
    CurriculumMessage, DayReviewMessage
from curriculum.models import Curriculum
from pagination import CustomPagination
from student.serializers import StudentDetailSerializer, StudentUserProfileSerializer
from teacher.serializers import TeacherDetailSerializer, TeacherProfileSerializer, TeacherUserProfileSerializer, \
    TeacherUserScheduleSerializer, CurriculumTeacherListerializer, DayReviewSerializer, DayReviewDetailSerializer
from utils import create_response_data, create_response_list_data, get_staff_total_attendance, \
    get_staff_monthly_attendance, get_staff_total_absent, get_staff_monthly_absent


class UserCreateView(APIView):
    permission_classes = [IsSuperAdminUser | IsAdminUser]
    """
    This class is used to create the user's for authentication.
    """

    def post(self, request):
        try:
            serializer = UserSignupSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            phone = serializer.validated_data['phone']
            user_type = serializer.validated_data['user_type']

            address_line_1 = serializer.validated_data['address_line_1']
            address_line_2 = serializer.validated_data['address_line_2']
            city = serializer.validated_data['city']
            state = serializer.validated_data['state']
            country = serializer.validated_data['country']
            pincode = serializer.validated_data['pincode']

            if user_type == 'admin':
                user = User.objects.create_admin_user(
                    name=name, email=email, password=password, phone=phone, user_type=user_type
                )
            elif user_type == 'management' or user_type == 'payrollmanagement' or user_type == 'boarding':
                user = User.objects.create_user(
                    name=name, email=email, password=password, phone=phone, user_type=user_type
                )
            else:
                raise ValidationError(
                    "Invalid user_type. Expected 'admin', 'management', 'payrollmanagement', 'boarding'.")
            user_address = AddressDetails.objects.create(
                user=user, address_line_1=address_line_1, address_line_2=address_line_2, city=city, state=state,
                country=country, pincode=pincode
            )
            response_data = {
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': str(user.phone),
                'is_email_verified': user.is_email_verified,
                'user_type': user.user_type
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


class FetchUserDetailView(APIView):
    permission_classes = [IsAdminUser | IsManagementUser | IsPayRollManagementUser | IsBoardingUser]
    """
    This class is used to fetch the detail of the user.
    """

    def get(self, request, pk):
        try:
            data = User.objects.get(id=pk)
            serializer = UsersListSerializer(data)
            resposne = create_response_data(
                status=status.HTTP_200_OK,
                message=UserResponseMessage.USER_DETAIL_MESSAGE,
                data=serializer.data,
            )
            return Response(resposne, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

#IsAdminUser
class UsersList(APIView):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    """
    This class is used to fetch the list of the user's.
    """

    def get(self, request):
        queryset = User.objects.all()
        if request.query_params:
            name = request.query_params.get('name', None)
            email = request.query_params.get("email", None)
            page = request.query_params.get('page_size', None)
            if name:
                queryset = queryset.filter(name__icontains=name)
            if email:
                queryset = queryset.filter(email__icontains=email)
            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializers = UsersListSerializer(paginated_queryset, many=True)
            response = create_response_list_data(
                status=status.HTTP_200_OK,
                count=len(serializers.data),
                message=UserResponseMessage.USER_LIST_MESSAGE,
                data=serializers.data,
            )
            return Response(response, status=status.HTTP_200_OK)
        serializer = UsersListSerializer(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_201_CREATED,
            count=len(serializer.data),
            message=UserLoginMessage.SIGNUP_SUCCESSFUL,
            data=serializer.data
        )
        return Response(response, status=status.HTTP_200_OK)


class UserDeleteView(APIView):
    permission_classes = [IsAdminUser]
    """
    This class is used to delete the user.
    """

    def delete(self, request, pk):
        try:
            user = User.objects.get(id=pk)
            user.is_active = False
            AddressDetails.objects.get(user_id=user.id)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=UserResponseMessage.USER_DELETE_MESSAGE,
                data={}
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class UserUpdateProfileView(APIView):
    permission_classes = [IsAdminUser]
    """
    This class is used to update the user profile.
    """

    def patch(self, request):
        serializer = UpdateProfileSerializer(request.user, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=UserResponseMessage.PROFILE_UPDATED_SUCCESSFULLY,
                data={}
            )
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=serializer.errors,
                data={}
            )
            return Response(response_data, status=status.HTTP_200_OK)

class LoginView(APIView):
    permission_classes = [permissions.AllowAny, ]
    """
    This class is used to login user's.
    """

    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
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
        refresh = RefreshToken.for_user(user)
        response_data = create_response_data(
            status=status.HTTP_201_CREATED,
            message=UserLoginMessage.SIGNUP_SUCCESSFUL,
            data={
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': str(user.phone),
                'is_email_verified': user.is_email_verified
            }
        )
        return Response(response_data, status=status.HTTP_201_CREATED)


class NonTeachingStaffCreateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to create non teaching staff type user's.
    """

    def post(self, request):
        try:
            serializer = NonTeachingStaffSerializers(data=request.data)
            serializer.is_valid(raise_exception=True)
            user_type = serializer.validated_data['user_type']
            image = serializer.validated_data['image']
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            gender = serializer.validated_data['gender']
            dob = serializer.validated_data['dob']
            blood_group = serializer.validated_data['blood_group']
            religion = serializer.validated_data['religion']
            email = serializer.validated_data['email']
            phone = serializer.validated_data['phone']
            role = serializer.validated_data['role']
            address = serializer.validated_data['address']
            joining_date = serializer.validated_data['joining_date']
            ctc = serializer.validated_data['ctc']
            certificates = serializer.validated_data.get('certificate_files', [])

            if serializer.is_valid() == True:
                if user_type == 'non-teaching' or user_type == 'management' or user_type == 'payrollmanagement' or user_type == 'boarding':
                    user = User.objects.create_user(
                        name=first_name, email=email, phone=phone, user_type=user_type, school_id=request.user.school_id
                    )
                    user.save()
                    user_staff = StaffUser.objects.create(
                        user=user, first_name=first_name, last_name=last_name, gender=gender, image=image, dob=dob, blood_group=blood_group,
                        religion=religion, role=role, address=address,
                        joining_date=joining_date, ctc=ctc,
                    )
                    for cert_file in certificates:
                        Certificate.objects.create(user=user, certificate_file=cert_file)
                else:
                    raise ValidationError("Invalid user_type. Expected 'teacher'.")
            else:
                response = create_response_data(
                    status=status.HTTP_201_CREATED,
                    message=serializer.errors,
                    data={}
                )
                return Response(response, status=status.HTTP_201_CREATED)
            response_data = {
                'user_id': user_staff.id,
                'name': user.first_name,
                'email': user.email,
                'phone': str(user.phone),
                'user_type': user.user_type,
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


class NonTeachingStaffListView(APIView):
    """
    This class is created to fetch the list of the non teaching staff.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        queryset = StaffUser.objects.filter(user__is_active=True, user__school_id=request.user.school_id)
        if request.query_params:
            name = request.query_params.get('first_name', None)
            page = request.query_params.get('page_size', None)
            if name:
                queryset = queryset.filter(first_name__icontains=name)

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializers = NonTeachingStaffListSerializers(paginated_queryset, many=True)
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

        serializer = NonTeachingStaffListSerializers(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_200_OK,
            count=len(serializer.data),
            message=UserResponseMessage.USER_LIST_MESSAGE,
            data=serializer.data,
        )
        return Response(response, status=status.HTTP_200_OK)


class NonTeachingStaffDetailView(APIView):
    """
    This class is created to fetch the detail of the non teaching staff.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            data = StaffUser.objects.get(id=pk, user__school_id=request.user.school_id)
            if data.user.is_active == True:
                serializer = NonTeachingStaffDetailSerializers(data)
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


class NonTeachingStaffDeleteView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to delete the non teaching staff.
    """

    def delete(self, request, pk):
        try:
            teacher = StaffUser.objects.get(id=pk, user__school_id=request.user.school_id)
            user = User.objects.get(id=teacher.user_id)
            if teacher.user.user_type == "non-teaching":
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
        except StaffUser.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class NonTeachingStaffUpdateView(APIView):
    """
    This class is used to update the non teaching staff.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def patch(self, request, pk):
        try:
            files_data = []
            certificate_files = request.data.getlist('certificate_files')

            for file in certificate_files:
                files_data.append(file)
            data = {
                'email': request.data.get('email'),
                'phone': request.data.get('phone'),
                'first_name': request.data.get('first_name'),
                'last_name': request.data.get('last_name'),
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
                'highest_qualification': request.data.get('highest_qualification'),
                'certificate_files': files_data
            }
            staff = StaffUser.objects.get(id=pk, user__school_id=request.user.school_id)
            serializer = NonTeachingStaffProfileSerializers(staff, data=data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()

                # Update certificates separately
                if files_data:
                    staff.user.certificates.all().delete()  # Delete existing certificates
                    for cert_file_data in files_data:
                        Certificate.objects.create(user=staff.user, certificate_file=cert_file_data)
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
        except StaffUser.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class AttendanceCreateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to marked non-teaching staff attendance.
    """
    def post(self, request):
        try:
            serializer = StaffAttendanceSerializer(data=request.data)
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
            staff = StaffUser.objects.get(id=pk)
            data = StaffAttendence.objects.filter(staff_id=pk).order_by('-date')

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
                serializer = StaffAttendanceDetailSerializer(data, many=True)
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=UserResponseMessage.USER_DETAIL_MESSAGE,
                    data={
                        "staff_name": f"{staff.first_name} {staff.last_name}",
                        "staff_id": staff.id,
                        "staff_role": staff.role,
                        "total_attendance": get_staff_total_attendance(data),
                        "monthly_attendance": get_staff_monthly_attendance(data),
                        "total_absent": get_staff_total_absent(data),
                        "monthly_absent": get_staff_monthly_absent(data),
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
        queryset = StaffUser.objects.filter(user__is_active=True)
        if request.query_params:
            name = request.query_params.get('first_name', None)
            page = request.query_params.get('page_size', None)
            if name:
                queryset = queryset.filter(first_name__icontains=name)

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializers = StaffAttendanceListSerializer(paginated_queryset, many=True)
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

        serializer = StaffAttendanceListSerializer(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_200_OK,
            count=len(serializer.data),
            message=UserResponseMessage.USER_LIST_MESSAGE,
            data=serializer.data,
        )
        return Response(response, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    This class is created to logout the login user.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            serializer = LogoutSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        except AuthenticationFailed as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'User logged out successfully'}, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    This class is created to fetch detail of the user profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            if user.user_type == 'teacher':
                teacher_user = TeacherUser.objects.get(user=user)
                user_detail = TeacherUserProfileSerializer(teacher_user)
            elif user.user_type == "student":
                student_user = StudentUser.objects.get(user=user)
                user_detail = StudentUserProfileSerializer(student_user)
            elif user.user_type == "non-teaching":
                staff_user = StaffUser.objects.get(user=user)
                user_detail = NonTeachingStaffDetailSerializers(staff_user)
        except (StudentUser.DoesNotExist, TeacherUser.DoesNotExist, StaffUser.DoesNotExist):
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response_data = create_response_data(
            status=status.HTTP_201_CREATED,
            message=UserLoginMessage.USER_LOGIN_SUCCESSFUL,
            data= user_detail.data
        )
        return Response(response_data, status=status.HTTP_201_CREATED)


class TeacherUserScheduleView(APIView):
    """
    This class is created to fetch schedule of the teacher.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            if user.user_type == 'teacher':
                today = datetime.date.today()
                teacher = TeacherUser.objects.get(user=user.id)
                data = TeachersSchedule.objects.filter(schedule_data__contains=[{"teacher": teacher.id}], start_date__lte=today, end_date__gte=today)
                if data:
                    serializer = TeacherUserScheduleSerializer(data[0])
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
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class TeacherCurriculumListView(APIView):
    """
    This class is created to fetch the list of classes, sections, and subject.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            if user.user_type == 'teacher':
                curriculum = Curriculum.objects.filter()
                serializer = CurriculumTeacherListerializer(curriculum, many=True)

                classes = list(set([item['class_name'] for item in serializer.data]))
                sections = list(set([item['section'] for item in serializer.data]))
                subject_names = list(set([subject['subject_name'] for item in serializer.data for subject in item['subject_name_code']]))

                response = {
                    'classes': classes,
                    'sections': sections,
                    'subjects': subject_names
                }
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=CurriculumMessage.CURRICULUM_LIST_MESSAGE,
                    data=response
                )
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="you are not an teacher user.",
                    data={}
                )
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TeacherDayReviewView(APIView):
    """
    This class is Used to create teacher day & review.
    """
    permission_classes = [IsTeacherUser, IsInSameSchool]

    def post(self, request):
        try:
            user = request.user
            if user.user_type == "teacher":

                serializer = DayReviewSerializer(data=request.data)
                if serializer.is_valid(raise_exception=True):
                    serializer.save(school_id=request.user.school_id)
                    response_data = create_response_data(
                        status=status.HTTP_201_CREATED,
                        message=DayReviewMessage.DAY_REVIEW_CREATED_SUCCESSFULLY,
                        data=serializer.data,
                    )
                    return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message='you are not an teacher user.',
                    data={}
                )
                return Response(response, status=status.HTTP_200_OK)
        except ValidationError as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_200_OK)


class TeacherDayReviewDetailView(APIView):
    """
    This colass is used to fetch detail of teacher day & review.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        try:
            data = DayReview.objects.get(id=pk, school_id=request.user.school_id)
            serializer = DayReviewDetailSerializer(data)
            response_data = create_response_data(
                        status=status.HTTP_201_CREATED,
                        message=DayReviewMessage.DAY_REVIEW_FETCHED_SUCCESSFULLY,
                        data=serializer.data,
                    )
            return Response(response_data, status=status.HTTP_200_OK)
        except DayReview.DoesNotExist:
            resposne = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=DayReviewMessage.DAY_REVIEW_NOT_FOUND,
                data={}
            )
            return Response(resposne, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class TeacherDayReviewListView(APIView):
    """
    This class is created to fetch the list of the teacher's day & review.
    """
    permission_classes = [IsTeacherUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        queryset = DayReview.objects.all()
        if request.query_params:
            updated_date = request.query_params.get('updated_date', None)
            if updated_date:
                queryset = queryset.filter(updated_date__gte=updated_date)

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializers = DayReviewDetailSerializer(paginated_queryset, many=True)
            response_data = {
                'status': status.HTTP_200_OK,
                'count': len(serializers.data),
                'message': ScheduleMessage.SCHEDULE_LIST_MESSAGE,
                'data': serializers.data,
            }
            return Response(response_data, status=status.HTTP_200_OK)

        serializer = DayReviewDetailSerializer(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_200_OK,
            count=len(serializer.data),
            message=ScheduleMessage.SCHEDULE_LIST_MESSAGE,
            data=serializer.data,
        )
        return Response(response, status=status.HTTP_200_OK)