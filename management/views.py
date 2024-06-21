from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import StaffUser
from authentication.permissions import IsInSameSchool, IsStaffUser
from constants import UserLoginMessage, UserResponseMessage
from management.serializers import ManagementProfileSerializer
from superadmin.models import SchoolProfile
from utils import create_response_data


# Create your views here.

class ManagementProfileView(APIView):
    """
    This class is used to fetch detail of management
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            if user.user_type == 'non-teaching':
                teacher_user = StaffUser.objects.get(user=user, user__school_id=request.user.school_id)
                user_detail = ManagementProfileSerializer(teacher_user)
        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        response_data = create_response_data(
            status=status.HTTP_201_CREATED,
            message=UserResponseMessage.USER_DETAIL_MESSAGE,
            data=user_detail.data
        )
        return Response(response_data, status=status.HTTP_201_CREATED)

