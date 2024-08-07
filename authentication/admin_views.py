from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsManagementUser, IsPayRollManagementUser, \
    IsBoardingUser, IsStaffUser, IsInSameSchool
from authentication.serializers import UserSignupSerializer, UsersListSerializer, UpdateProfileSerializer, \
    UserLoginSerializer, StaffProfileSerializer, StaffUpdateProfileSerializer, StaffSignupSerializer
from pagination import CustomPagination
from utils import create_response_data, create_response_list_data
from django.db import IntegrityError
from rest_framework import status, permissions, response
from rest_framework.exceptions import ValidationError
from authentication.models import User, AddressDetails, StudentUser, TeacherUser, StaffUser
from constants import UserLoginMessage, UserResponseMessage
from rest_framework.response import Response


class AdminStaffLoginView(APIView):
    permission_classes = [permissions.AllowAny, ]
    """
    This class is used to login user's.
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
            role = None
            if user.user_type in ['non-teaching', 'management', 'payrollmanagement']:
                try:
                    staff_user = StaffUser.objects.get(user=user)
                    role = staff_user.role
                except StaffUser.DoesNotExist:
                    role = None

            refresh = RefreshToken.for_user(user)
            response_data = create_response_data(
                status=status.HTTP_201_CREATED,
                message=UserLoginMessage.USER_LOGIN_SUCCESSFUL,
                data={
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user_id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'phone': str(user.phone),
                    'user_type': user.user_type,
                    'role': role
                }
            )
            return Response(response_data, status=status.HTTP_201_CREATED)
        except ValidationError:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors,
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class UserListView(APIView):
    """
    This class is used to fetch all user's list.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        try:
            student = StudentUser.objects.filter(user__is_active=True, user__school_id=request.user.school_id)
            teacher = TeacherUser.objects.filter(user__is_active=True, user__school_id=request.user.school_id)
            staff = StaffUser.objects.filter(user__is_active=True, user__school_id=request.user.school_id)
            data = {
                "student": len(student),
                "teacher": len(teacher),
                "staff": len(staff),
            }
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=UserResponseMessage.USER_LIST_MESSAGE,
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


class StaffProfileView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        serializer = StaffProfileSerializer(request.user)
        response_data = create_response_data(
            status=status.HTTP_200_OK,
            message="",
            data=serializer.data
        )
        return Response(response_data, status=status.HTTP_200_OK)


class GetStaffView(APIView):
    permission_classes = [IsSuperAdminUser,]

    def get(self, request, pk):
        instance = User.objects.get(id=pk)
        if instance.is_staff == False:
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=UserLoginMessage.NOT_STAFF_USER,
                data={}
            )
            return Response(response_data, status=status.HTTP_200_OK)
        serializer = StaffProfileSerializer(instance)
        response_data = create_response_data(
            status=status.HTTP_200_OK,
            message=UserResponseMessage.USER_DETAIL_MESSAGE,
            data=serializer.data
        )
        return Response(response_data, status=status.HTTP_200_OK)


class StaffUpdateProfileView(APIView):
    permission_classes = [IsSuperAdminUser,]

    def patch(self, request, pk):
        user = User.objects.get(id=pk, is_staff=True)
        if not user:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_NOT_FOUND,
                data={}
            )
            return response.Response(response_data, status=status.HTTP_404_NOT_FOUND)

        serializer = StaffUpdateProfileSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_data = create_response_data(
            status=status.HTTP_200_OK,
            message=UserResponseMessage.PROFILE_UPDATED_SUCCESSFULLY,
            data=StaffProfileSerializer(user).data
        )
        return Response(response_data, status=status.HTTP_200_OK)


class AdminStaffDeleteView(APIView):
    permission_classes = [IsSuperAdminUser,]

    def delete(self, request, pk):
        user = User.objects.get(id=pk, is_staff=True)
        resp_status = status.HTTP_404_NOT_FOUND
        message = UserResponseMessage.USER_NOT_FOUND
        if user:
            user.is_active = False
            user.save()
            resp_status = status.HTTP_200_OK
            message = UserResponseMessage.USER_DELETE_MESSAGE

        response_data = create_response_data(
            status=resp_status,
            message=message,
            data={}
        )
        return Response(response_data, status=resp_status)


class AdminStaffCreateView(APIView):
    permission_classes = [IsSuperAdminUser, ]

    def post(self, request):
        serializer = StaffSignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data['name']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        phone = serializer.validated_data['phone']
        user_type = serializer.validated_data['user_type']
        school_id = serializer.validated_data['school_id']
        try:
            user = User.objects.create_admin_user(
                name=name, email=email, password=password, phone=phone, user_type=user_type, is_staff=True, school_id=school_id
            )
        except IntegrityError:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.STAFF_ALREADY_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        response_data = create_response_data(
            status=status.HTTP_201_CREATED,
            message=UserLoginMessage.SIGNUP_SUCCESSFUL,
            data={
                'user_id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': str(user.phone),
                'is_email_verified': user.is_email_verified
            }
        )
        return Response(response_data, status=status.HTTP_201_CREATED)
