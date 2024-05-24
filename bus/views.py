from django.db.models import Q
from django.shortcuts import render

from authentication.models import StaffUser
from pagination import CustomPagination
from .models import Route, Bus
from .serializers import RouteSerializer, BusSerializer, BusListSerializer, BusDetailSerializer, RouteListSerializer
from rest_framework import status, permissions, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.permissions import IsSuperAdminUser, IsAdminUser, IsManagementUser, IsPayRollManagementUser, \
    IsBoardingUser, IsInSameSchool, IsTeacherUser
from utils import create_response_data, create_response_list_data
from constants import BusMessages

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
    
class CreateBusView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    def post(self, request):
        serializer = BusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(school_id=request.user.school_id)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=BusMessages.BUS_ADDED,
                data=serializer.data,
            )
            return Response(response_data, status=status.HTTP_200_OK)
        response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors,
                data={},
            )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
class BusListView(generics.ListAPIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    def get(self, request):
        queryset = Bus.objects.filter(school_id=request.user.school_id).select_related('driver_name', 'operator_name', 'bus_route', 'alternate_route')
        serializer = BusListSerializer(queryset, many=True)
        response_data = create_response_data(
            status=status.HTTP_200_OK,
            message=BusMessages.BUS_DATA_FETCHED,
            data=serializer.data,
        )
        return Response(response_data, status=status.HTTP_200_OK)
    
class BusDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get_queryset(self):
        return Bus.objects.filter(school_id=self.request.user.school_id)

    def delete(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            self.perform_destroy(instance)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=BusMessages.BUS_DELETED,
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


class BusDetailView(APIView):
    """
    This class is used to fetch the detail of the bus.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request,pk):
        try:
            bus_detail = Bus.objects.get(school_id=request.user.school_id, id=pk)
            serializer = BusDetailSerializer(bus_detail)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=BusMessages.BUS_DATA_FETCHED,
                data=serializer.data,
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Bus.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=BusMessages.BUS_NOT_FOUND,
                data={},
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class BusRouteListView(APIView):
    """
    This class is used to fetch list of the bus route.
    """
    permission_classes = [IsAdminUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            bus_route = Route.objects.filter(school_id=request.user.school_id).order_by('-id')
            search = self.request.query_params.get('search', None)
            if search is not None:
                bus_route = bus_route.filter(Q(id__icontains=search) | Q(name__icontains=search))
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(bus_route, request)

            serializers = RouteListSerializer(paginated_queryset, many=True)
            response_data = {
                'status': status.HTTP_200_OK,
                'count': len(serializers.data),
                'message': BusMessages.ROUTE_DATA_FETCHED,
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
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class BusRouteDetailView(APIView):
    """
    This class is used to fetch detail of the bus route.
    """

    permission_classes = [IsAdminUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            bus_route = Route.objects.get(school_id=request.user.school_id, id=pk)
            serializer = RouteListSerializer(bus_route)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=BusMessages.ROUTE_DATA_FETCHED,
                data=serializer.data,
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Route.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=BusMessages.BUS_ROUTE_NOT_FOUND,
                data={},
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class BusRouteDeleteView(APIView):
    """
    This class is used to delete the bus route detail.
    """

    permission_classes = [IsAdminUser, IsInSameSchool]

    def delete(self, request, pk):
        try:
            bus_route = Route.objects.get(school_id=request.user.school_id, id=pk)
            bus_route.delete()
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=BusMessages.BUS_ROUTE_DELETED,
                data={},
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Route.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=BusMessages.BUS_ROUTE_NOT_FOUND,
                data={},
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
