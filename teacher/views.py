from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User, Class, TeacherUser, StudentUser
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsTeacherUser
from constants import UserLoginMessage, UserResponseMessage
from pagination import CustomPagination
from teacher.serializers import TeacherUserSignupSerializer, TeacherDetailSerializer, TeacherListSerializer, \
    TeacherProfileSerializer
from utils import create_response_data, create_response_list_data


# Create your views here.

class TeacherUserCreateView(APIView):
    permission_classes = [IsSuperAdminUser | IsAdminUser]
    """
    This class is used to create teacher type user's.
    """

    def post(self, request):
        try:
            serializer = TeacherUserSignupSerializer(data=request.data)
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

            dob = serializer.validated_data['dob']
            image = serializer.validated_data['image']
            gender = serializer.validated_data['gender']
            first_name = serializer.validated_data['first_name']
            last_name = serializer.validated_data['last_name']
            joining_date = serializer.validated_data['joining_date']
            religion = serializer.validated_data['religion']
            blood_group = serializer.validated_data['blood_group']
            salary = serializer.validated_data['salary']

            class_name = serializer.validated_data['class_name']
            section = serializer.validated_data['section']

            if user_type == 'teacher' and serializer.is_valid() == True:
                user = User.objects.create_user(
                    name=name, email=email, password=password, phone=phone, user_type=user_type
                )
                user_address = AddressDetails.objects.create(
                    user=user, address_line_1=address_line_1, address_line_2=address_line_2, city=city, state=state,
                    country=country, pincode=pincode
                )
                class_info = Class.objects.create(
                    class_name=class_name, section=section
                )
                user_teacher = TeacherUser.objects.create(
                    user=user, dob=dob, image=image, gender=gender, joining_date=joining_date, first_name=first_name,
                    religion=religion, blood_group=blood_group, salary=salary, last_name=last_name
                )
                user_teacher.class_taught.add(class_info)
            else:
                raise ValidationError("Invalid user_type. Expected 'teacher'.")
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


class FetchTeacherDetailView(APIView):
    """
    This class is created to fetch the detail of the teacher.
    """
    permission_classes = [IsAdminUser | IsTeacherUser]

    def get(self, request, pk):
        try:
            data = TeacherUser.objects.get(id=pk)
            serializer = TeacherDetailSerializer(data)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=UserResponseMessage.USER_DETAIL_MESSAGE,
                data=serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except TeacherUser.DoesNotExist:
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
        queryset = TeacherUser.objects.all()
        if request.query_params:
            name = request.query_params.get('name', None)
            page = request.query_params.get('page_size', None)
            if name:
                queryset = queryset.filter(user__name__icontains=name)

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializers = TeacherListSerializer(paginated_queryset, many=True)
            response = create_response_list_data(
                status=status.HTTP_200_OK,
                count=len(serializers.data),
                message=UserResponseMessage.USER_LIST_MESSAGE,
                data=serializers.data,
            )
            return Response(response, status=status.HTTP_200_OK)

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
    """
    This class is used to update the teacher profile.
    """

    def patch(self, request, pk):
        try:
            teacher = TeacherUser.objects.get(id=pk)
            serializer = TeacherProfileSerializer(teacher, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                # Update related Class instances if provided
                class_name = serializer.validated_data.get('class_name')
                section = serializer.validated_data.get('section')
                if class_name or section:
                    teacher = Class.objects.get_or_create(class_name=class_name, section=section)
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
        except User.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)