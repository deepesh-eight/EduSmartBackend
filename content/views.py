from django.shortcuts import render
from django.db.models import Q
from rest_framework.exceptions import ValidationError

from pagination import CustomPagination
from .models import Content
from .serializers import ContentSerializer, ContentListSerializer, ContentUpdateSerializer
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsManagementUser, IsPayRollManagementUser, \
    IsBoardingUser, IsInSameSchool, IsTeacherUser, IsStudentUser
from utils import create_response_data, create_response_list_data
from constants import ContentMessages

class SuperAdminContentCreateView(APIView):
    permission_classes = [IsSuperAdminUser]
    def post(self, request, format=None):
        serializer = ContentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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

class ContentCreateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    def post(self, request, format=None):
        try:
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
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
class ContentListView(generics.ListAPIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Content.objects.filter(Q(school_id=self.request.user.school_id) | Q(school_id__isnull=True)).order_by('-id')
        content_type = self.request.query_params.get('content_type', None)
        is_recommended = self.request.query_params.get('is_recommended', None)
        if content_type is not None:
            queryset = queryset.filter(content_type=content_type)
        if is_recommended is not None:
            queryset = queryset.filter(is_recommended=is_recommended)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = ContentListSerializer(paginated_queryset, many=True)
        response_data = {
            'status': status.HTTP_200_OK,
            'count': len(serializer.data),
            'message': ContentMessages.CONTENT_FETCHED,
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
        
class StudentContentListView(generics.ListAPIView):
    permission_classes = [IsStudentUser, IsInSameSchool]

    def get_queryset(self):
        queryset = Content.objects.filter(Q(school_id=self.request.user.school_id) | Q(school_id__isnull=True)).order_by('-id')
        content_type = self.request.query_params.get('content_type', None)
        is_recommended = self.request.query_params.get('is_recommended', None)
        if content_type is not None:
            queryset = queryset.filter(content_type=content_type)
        if is_recommended is not None:
            queryset = queryset.filter(is_recommended=is_recommended)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = ContentListSerializer(queryset, many=True)
        response_data = create_response_data(
            status=status.HTTP_200_OK,
            message=ContentMessages.CONTENT_FETCHED,
            data=serializer.data,
        )
        return Response(response_data, status=status.HTTP_200_OK)


class ContentUpdateView(APIView):
    """
    This class is used to update the book content.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def patch(self, request, pk):
        try:
            school_data = Content.objects.get(id=pk, school_id=request.user.school_id)
            serializer = ContentUpdateSerializer(school_data, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=ContentMessages.CONTENT_UPDATED,
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
        except Content.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=ContentMessages.CONTENT_NOT_EXIST,
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