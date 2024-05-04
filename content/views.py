from django.shortcuts import render
from .models import Content
from .serializers import ContentSerializer
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsManagementUser, IsPayRollManagementUser, \
    IsBoardingUser, IsInSameSchool, IsTeacherUser
from utils import create_response_data, create_response_list_data
from constants import ContentMessages

class ContentCreateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    def post(self, request, format=None):
        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(school_id=request.user.school_id)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=ContentMessages.CONTENT_CREATED,
                data=serializer.data,
            )
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = create_response_data(
            status=status.HTTP_400_BAD_REQUEST,
            message=serializer.errors,
            data={},
        )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
class ContentListView(generics.ListAPIView):
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get_queryset(self):
        queryset = Content.objects.filter(school_id=self.request.user.school_id)
        content_type = self.request.query_params.get('content_type', None)
        if content_type is not None:
            queryset = queryset.filter(content_type=content_type)
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ContentSerializer(queryset, many=True)
        response_data = create_response_data(
            status=status.HTTP_200_OK,
            message=ContentMessages.CONTENT_FETCHED,
            data=serializer.data,
        )
        return Response(response_data, status=status.HTTP_200_OK)
    
class ContentDeleteView(generics.DestroyAPIView):
    serializer_class = ContentSerializer
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get_queryset(self):
        return Content.objects.filter(school_id=self.request.user.school_id)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message="Content successfully deleted.",
                data={}
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
