import json

from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import User, Class, TeacherUser, StudentUser, Certificate
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
                user_teacher = TeacherUser.objects.create(
                    user=user, dob=dob, image=image, gender=gender, joining_date=joining_date, full_name=full_name,
                    religion=religion, blood_group=blood_group, ctc=ctc,
                    experience=experience, role=role, address=address,
                    class_subject_section_details=class_subject_section_details,
                    highest_qualification=highest_qualification,
                )
                for cert_file in certificates:
                    Certificate.objects.create(teacher=user_teacher, certificate_file=cert_file)
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
                    message=f"{data.full_name} does not exist.",
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
        queryset = TeacherUser.objects.all()
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
                    teacher.certificates.all().delete()  # Delete existing certificates
                    for cert_file_data in files_data:
                        Certificate.objects.create(teacher=teacher, certificate_file=cert_file_data)
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
        except User.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)