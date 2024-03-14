from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User, Class, AddressDetails, StudentUser
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsStudentUser
from constants import UserLoginMessage, UserResponseMessage
from pagination import CustomPagination
from student.serializers import StudentUserSignupSerializer, StudentDetailSerializer, StudentListSerializer, \
    studentProfileSerializer
from utils import create_response_data, create_response_list_data


class StudentUserCreateView(APIView):
    permission_classes = [IsSuperAdminUser | IsAdminUser]
    """
    This class is used to create student type user's.
    """

    def post(self, request):
        try:
            serializer = StudentUserSignupSerializer(data=request.data)
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
            father_name = serializer.validated_data['father_name']
            mother_name = serializer.validated_data['mother_name']
            gender = serializer.validated_data['gender']
            father_occupation = serializer.validated_data['father_occupation']
            admission_date = serializer.validated_data['admission_date']
            religion = serializer.validated_data['religion']
            school_fee = serializer.validated_data['school_fee']
            bus_fee = serializer.validated_data['bus_fee']
            canteen_fee = serializer.validated_data['canteen_fee']
            other_fee = serializer.validated_data['other_fee']
            total_amount = serializer.validated_data['total_amount']
            blood_group = serializer.validated_data['blood_group']

            class_name = serializer.validated_data['class_name']
            section = serializer.validated_data['section']

            if user_type == 'student' and serializer.is_valid() == True:
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
                user_student = StudentUser.objects.create(
                    user=user, dob=dob, image=image, father_name=father_name, mother_name=mother_name,
                    gender=gender, father_occupation=father_occupation, religion=religion,
                    admission_date=admission_date,
                    school_fee=school_fee, bus_fee=bus_fee, canteen_fee=canteen_fee, other_fee=other_fee,
                    total_amount=total_amount, blood_group=blood_group, class_enrolled=class_info
                )
            else:
                raise ValidationError("Invalid user_type. Expected 'student'.")
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


class FetchStudentDetailView(APIView):
    """
    This class is created to fetch the detail of the student.
    """
    permission_classes = [IsAdminUser | IsStudentUser]

    def get(self, request, pk):
        try:
            data = StudentUser.objects.get(id=pk)
            serializer = StudentDetailSerializer(data)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=UserResponseMessage.USER_DETAIL_MESSAGE,
                data=serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)
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
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination

    def get(self, request):
        queryset = StudentUser.objects.all()
        if request.query_params:
            name = request.query_params.get('name', None)
            father_name = request.query_params.get('father_name', None)
            page = request.query_params.get('page_size', None)
            if name:
                queryset = queryset.filter(user__name__icontains=name)
            if father_name:
                queryset = queryset.filter(father_name__icontains=father_name)

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)

            serializers = StudentListSerializer(paginated_queryset, many=True)
            response = create_response_list_data(
                status=status.HTTP_200_OK,
                count=len(serializers.data),
                message=UserResponseMessage.USER_LIST_MESSAGE,
                data=serializers.data,
            )
            return Response(response, status=status.HTTP_200_OK)

        serializer = StudentListSerializer(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_200_OK,
            count=len(serializer.data),
            message=UserResponseMessage.USER_LIST_MESSAGE,
            data=serializer.data,
        )
        return Response(response, status=status.HTTP_200_OK)


class StudentDeleteView(APIView):
    permission_classes = [IsAdminUser]
    """
    This class is used to delete the student.
    """

    def delete(self, request, pk):
        try:
            student = StudentUser.objects.get(id=pk)
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
    permission_classes = [IsAdminUser]
    """
    This class is used to update the student profile.
    """

    def patch(self, request, pk):
        try:
            student = StudentUser.objects.get(id=pk)
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
        except User.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)