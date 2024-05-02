from django.shortcuts import render
from .models import Route
from .serializers import RouteSerializer
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsManagementUser, IsPayRollManagementUser, \
    IsBoardingUser, IsInSameSchool, IsTeacherUser
from utils import create_response_data, create_response_list_data
from constants import BusMessages

class RouteListView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    def get(self, request):
        queryset = Route.objects.filter(school_id=request.user.school_id)
        serializer = RouteSerializer(queryset, many=True)
        response_data = create_response_data(
            status=status.HTTP_200_OK,
            message=BusMessages.ROUTE_DATA_FETCHED,
            data=serializer.data,
        )
        return Response(response_data, status=status.HTTP_200_OK)

class RouteCreateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    def post(self, request):
        serializer = RouteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(school_id=request.user.school_id)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=BusMessages.BUS_ROUTE_CREATED,
                data=serializer.data,
            )
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors,
                data={},
            )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)