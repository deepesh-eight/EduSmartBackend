from django.db import IntegrityError
from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from authentication.models import User, AddressDetails, ErrorLogging
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsManagementUser, IsPayRollManagementUser, \
    IsBoardingUser
from authentication.serializers import UserSignupSerializer, UsersListSerializer, UpdateProfileSerializer, \
    UserLoginSerializer
from constants import UserLoginMessage, UserResponseMessage
from pagination import CustomPagination
from utils import create_response_data, create_response_list_data


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
            ErrorLogging.exception.error_messages(f'user does not exist {User}')
            resposne = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(resposne, status=status.HTTP_400_BAD_REQUEST)
        if not user.check_password(password):
            ErrorLogging.exception.error_messages(f'{UserLoginMessage.INCORRECT_PASSWORD}')
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
