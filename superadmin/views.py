import json

from django.db import IntegrityError
from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from authentication.models import User
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsInSameSchool
from constants import SchoolMessage, UserLoginMessage, UserResponseMessage, CurriculumMessage
from pagination import CustomPagination
from superadmin.models import SchoolProfile, CurricullumList
from superadmin.serializers import SchoolCreateSerializer, SchoolProfileSerializer, SchoolProfileUpdateSerializer, \
    CurriculumCreateSerializer, CurriculumListSerializer, CurriculumUpdateSerializer
from utils import create_response_data


# Create your views here.

class SchoolCreateView(APIView):
    permission_classes = [IsSuperAdminUser]
    """
    This class is used to create school.
    """
    def post(self, request):
        try:
            serializer = SchoolCreateSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            name = serializer.validated_data.get('principle_name', '')
            email = serializer.validated_data.get('email', '')
            user_type = serializer.validated_data.get('user_type', '')
            phone = serializer.validated_data.get('contact_no', '')
            school_id = serializer.validated_data.get('school_id', '')
            password = serializer.validated_data.get('password', '')

            logo = serializer.validated_data['logo']
            school_name = serializer.validated_data.get('school_name', '')
            address = serializer.validated_data.get('address', '')
            city = serializer.validated_data.get('city', '')
            state = serializer.validated_data.get('state', '')
            established_year = serializer.validated_data.get('established_year', '')
            school_type = serializer.validated_data.get('school_type', '')
            school_website = serializer.validated_data.get('school_website', '')
            description = serializer.validated_data.get('description', '')
            if user_type == 'admin' and serializer.is_valid() == True:
                user = User.objects.create_admin_user(
                    name=name, email=email, user_type=user_type, school_id=school_id, phone=phone, password=password
                )
                school_detail = SchoolProfile.objects.create(
                    user=user, logo=logo, school_name=school_name, address=address, city=city, state=state,
                    established_year=established_year, school_type=school_type, school_website=school_website,
                    description=description, principle_name=name, password=password, contact_no=phone, email=email,
                    school_id=school_id
                )
            else:
                raise ValidationError("Invalid user_type. Expected 'admin'.")
            response = create_response_data(
                status=status.HTTP_201_CREATED,
                message=SchoolMessage.SCHOOL_CREATED_SUCCESSFULLY,
                data={
                    'user_id': user.id,
                    'school_id': user.school_id,
                    'principle_name': user.name,
                    'school_name': school_detail.school_name,
                    'password': school_detail.password
                }
            )
            return Response(response, status=status.HTTP_200_OK)
        except IntegrityError:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserResponseMessage.EMAIL_ALREADY_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors,
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class SchoolProfileView(APIView):
    permission_classes = [IsSuperAdminUser,]
    """
    This class is created to fetch profile of the school.
    """
    def get(self, request, pk):
        try:
            data = SchoolProfile.objects.get(id=pk)
            serializer = SchoolProfileSerializer(data)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=SchoolMessage.SCHOOL_DETAIL_MESSAGE,
                data=serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=SchoolMessage.SCHOOL_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class SchoolProfileUpdateView(APIView):
    """
    This class is created to update profile of the school.
    """
    permission_classes = [IsSuperAdminUser]

    def patch(self, request, pk):
        try:
            school_data = SchoolProfile.objects.get(id=pk)
            serializer = SchoolProfileUpdateSerializer(school_data, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=SchoolMessage.SCHOOL_PROFILE_UPDATED_SUCCESSFULLY,
                    data={}
                )
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data=serializer.errors
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except SchoolProfile.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=SchoolMessage.SCHOOL_DOES_NOT_EXISTS,
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
        except IntegrityError:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=SchoolMessage.SCHOOL_EMAIL_ALREADY_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class SchoolAdminProfileView(APIView):
    """
    This class is created to view school profile.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            if user.user_type == 'admin':
                teacher_user = SchoolProfile.objects.get(user=user)
                user_detail = SchoolProfileSerializer(teacher_user)
        except SchoolProfile.DoesNotExist:
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


class SchoolAdminListView(APIView):
    """
    This class is created to fetch list of school's.
    """
    permission_classes = [IsSuperAdminUser]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            data = SchoolProfile.objects.all().order_by('-id')
            if request.query_params:
                school_name = request.query_params.get('school_name', None)
                if school_name:
                    data = data.filter(school_name=school_name)
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(data, request)
            serializer = SchoolProfileSerializer(paginated_queryset, many=True)
            response_data = {
                'status': status.HTTP_200_OK,
                'count': len(serializer.data),
                'message': SchoolMessage.SCHOOL_DETAIL_MESSAGE,
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
            create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class SchoolAdminDeleteView(APIView):
    """
    This class is used to delete school profile.
    """
    permission_classes = [IsSuperAdminUser]

    def delete(self, request, pk):
        try:
            school_profile = SchoolProfile.objects.get(id=pk)
            school_profile.delete()
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=SchoolMessage.SCHOOL_DELETED_SCCCESSFULLY,
                data={}
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except SchoolProfile.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=SchoolMessage.SCHOOL_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class CurriculumCreateView(APIView):
    """
    This class is used to create curriculum from the superadmin.
    """
    permission_classes = [IsSuperAdminUser]

    def post(self, request):
        try:
            serializer = CurriculumCreateSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response_data = create_response_data(
                status=status.HTTP_201_CREATED,
                message=CurriculumMessage.CURRICULUM_CREATED_SUCCESSFULLY,
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
        except ValidationError as er:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(er.detail.get('non_field_errors')[0]),
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


class CurriculumListView(APIView):
    """
    This class is used to fetch the list of the curriculum.
    """
    permission_classes = [IsSuperAdminUser]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            data = CurricullumList.objects.all().order_by('-id')
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(data, request)
            serializer = CurriculumListSerializer(paginated_queryset, many=True)
            response_data = {
                'status': status.HTTP_200_OK,
                'count': len(serializer.data),
                'message': CurriculumMessage.CURRICULUM_LIST_MESSAGE,
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


class CurriculumDetailView(APIView):
    """
    This class is used to fetch detail of curriculum which is added by superadmin
    """
    permission_classes = [IsSuperAdminUser]

    def get(self, request, pk):
        try:
            data = CurricullumList.objects.get(id=pk)
            serializer = CurriculumListSerializer(data)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.CURRICULUM_DETAIL_MESSAGE,
                data=serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except CurricullumList.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=CurriculumMessage.CURRICULUM_NOT_FOUND,
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


class CurriculumUpdateView(APIView):
    """
    This class is used to fetch detail of curriculum which is added by superadmin
    """
    permission_classes = [IsSuperAdminUser]

    def patch(self, request, pk):
        try:
            data = CurricullumList.objects.get(id=pk)
            serializer = CurriculumUpdateSerializer(data, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=CurriculumMessage.CURRICULUM_UPDATED_MESSAGE,
                    data=serializer.data
                )
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data={}
                )
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except CurricullumList.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=CurriculumMessage.CURRICULUM_NOT_FOUND,
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


class CurriculumDeleteView(APIView):
    """
    This class is used to delete the curriculum by superadmin.
    """
    permission_classes = [IsSuperAdminUser]

    def delete(self, request, pk):
        try:
            data = CurricullumList.objects.get(id=pk)
            data.delete()
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.CURRICULUM_DELETED_SUCCESSFULLY,
                data={}
            )
            return Response(response_data, status=status.HTTP_200_OK)

        except CurricullumList.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=CurriculumMessage.CURRICULUM_NOT_FOUND,
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