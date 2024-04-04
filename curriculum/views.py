from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.permissions import IsAdminUser
from constants import CurriculumMessage
from curriculum.models import Curriculum
from curriculum.serializers import CurriculumSerializer
from pagination import CustomPagination
from utils import create_response_data


# Create your views here.


class CurriculumCreateView(APIView):
    permission_classes = [IsAdminUser]
    """
    This class is used to create curriculum.
    """
    def post(self,request):
        serializer = CurriculumSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            response = create_response_data(
                status=status.HTTP_201_CREATED,
                message=CurriculumMessage.CURRICULUM_CREATED_SUCCESSFULLY,
                data=serializer.data
            )
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=serializer.errors,
                data=serializer.errors
            )
            return Response(response, status=status.HTTP_200_OK)

class CurriculumlistView(APIView):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    """
    This class is created to fetch the list of the curriculum.
    """
    def get(self,request):
        queryset = Curriculum.objects.all()
        paginator = self.pagination_class()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        serializer = CurriculumSerializer(paginated_queryset, many=True)
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