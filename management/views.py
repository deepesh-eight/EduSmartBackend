from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import StaffUser, TimeTable
from authentication.permissions import IsInSameSchool, IsStaffUser
from constants import UserLoginMessage, UserResponseMessage, TimeTableMessage
from management.serializers import ManagementProfileSerializer, TimeTableSerializer
from pagination import CustomPagination
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
                teacher_user = StaffUser.objects.get(user=user, user__school_id=request.user.school_id, role="Payroll Management")
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


class CurrentExamTimeTableView(APIView):
    """
    This class is used to fetch current exam timetable.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            current_date = timezone.now().date()
            teacher_user = StaffUser.objects.get(user=user, user__school_id=request.user.school_id,
                                                 role="Payroll Management")
            exam_timetable = TimeTable.objects.filter(status=1, school_id=user.school_id, exam_month__gte=str(current_date)).order_by('-id')

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(exam_timetable, request)

            serializers = TimeTableSerializer(paginated_queryset, many=True)
            response = {
                'status': status.HTTP_201_CREATED,
                'count': len(serializers.data),
                'message': TimeTableMessage.DECLARED_TIMETABLE_FETCHED_SUCCESSFULLY,
                'data': serializers.data,
                'pagination': {
                    'page_size': paginator.page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': paginator.page.number,
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)