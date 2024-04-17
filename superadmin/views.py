from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from authentication.permissions import IsSuperAdminUser
from constants import SchoolMessage
from superadmin.models import SchoolProfile
from superadmin.serializers import SchoolCreateSerializer, SchoolProfileSerializer
from utils import create_response_data


# Create your views here.

class SchoolCreateView(APIView):
    permission_classes = [IsSuperAdminUser]
    """
    This class is used to create school.
    """
    def post(self, request):
        serializer = SchoolCreateSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response = create_response_data(
                status=status.HTTP_201_CREATED,
                message=SchoolMessage.SCHOOL_CREATED_SUCCESSFULLY,
                data={}
            )
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors,
                data=serializer.errors
            )
            return Response(response, status=status.HTTP_200_OK)


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