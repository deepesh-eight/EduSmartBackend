from django.db import IntegrityError
from django.shortcuts import render
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from authentication.models import User
from authentication.permissions import IsSuperAdminUser
from constants import SchoolMessage
from superadmin.models import SchoolProfile
from superadmin.serializers import SchoolCreateSerializer, SchoolProfileSerializer, SchoolProfileUpdateSerializer
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
                message="Email already exist.",
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as exp:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=exp.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=f"Missing key in request data: {e}",
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
                    status=status.HTTP_200_OK,
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
                message=SchoolMessage.SCHOOL_EMAIL_ALREADY_EXIST,
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
