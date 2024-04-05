from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from EduSmart import settings
from authentication.permissions import IsAdminUser
from constants import CurriculumMessage
from curriculum.models import Curriculum, CurriculumPDF
from curriculum.serializers import CurriculumSerializer, CurriculumDetailSerializer, CurriculumUploadSerializer
from pagination import CustomPagination
from utils import create_response_data, create_response_list_data


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

class CurriculumUploadView(APIView):
    permission_classes = [IsAdminUser]
    """
    This class is used to upload curriculum.
    """
    def post(self,request):
        try:
            serializer = CurriculumUploadSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            academic_session = serializer.validated_data.get('academic_session', '')
            exam_board = serializer.validated_data.get('exam_board', '')
            class_name = serializer.validated_data.get('class_name', '')
            section = serializer.validated_data.get('section', '')
            subject_name_code = serializer.validated_data.get('subject_name_code', '')
            curriculum_pdf_file = serializer.validated_data.get('curriculum_pdf_file', '')
            create_curriculum = Curriculum.objects.create(
                academic_session=academic_session, exam_board=exam_board, class_name=class_name, section=section, subject_name_code=subject_name_code)
            upload_curriculum = CurriculumPDF.objects.create(curriculum=create_curriculum, curriculum_pdf_file=curriculum_pdf_file)
            response_data = {
                'id': create_curriculum.id,
                'academic_session': create_curriculum.academic_session,
                'exam_board': create_curriculum.exam_board,
                'class_name': create_curriculum.class_name,
                'section': create_curriculum.section,
                'subject_name_code': create_curriculum.subject_name_code,
            }
            response = create_response_data(
                status=status.HTTP_201_CREATED,
                message=CurriculumMessage.CURRICULUM_CREATED_SUCCESSFULLY,
                data=response_data
            )
            return Response(response, status=status.HTTP_201_CREATED)

        except KeyError as e:
            return Response(f"Missing key in request data: {e}", status=status.HTTP_400_BAD_REQUEST)

class CurriculumlistView(APIView):
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    """
    This class is created to fetch the list of the curriculum.
    """
    def get(self,request):
        queryset = Curriculum.objects.all()
        for curriculum in queryset:
            if not curriculum.curriculum_name:
                querset1 = CurriculumPDF.objects.all()
                for pdf_data in querset1:
                    curriculum.curriculum_name = f"{settings.base_url}{settings.MEDIA_URL}{pdf_data.curriculum_pdf_file}"
                    curriculum.save()
        if request.query_params:
            academic_session = request.query_params.get('academic_session', None)
            class_name = request.query_params.get('class_name', None)
            if academic_session:
                queryset = queryset.filter(academic_session__icontains=academic_session)
            if class_name:
                queryset = queryset.filter(class_name__icontains=class_name)
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
        serializer = CurriculumSerializer(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_200_OK,
            count=len(serializer.data),
            message=CurriculumMessage.CURRICULUM_LIST_MESSAGE,
            data=serializer.data,
        )
        return Response(response, status=status.HTTP_200_OK)


class CurriculumDeleteView(APIView):
    permission_classes = [IsAdminUser]
    """
    This class is created to delete the curriculum.
    """
    def delete(self, request, pk):
        try:
            curriculum_detail = Curriculum.objects.get(id=pk)
            curriculum_detail.delete()
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.CURRICULUM_DELETED_SUCCESSFULLY,
                data={}
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Curriculum.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=CurriculumMessage.CURRICULUM_NOT_FOUND,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

class CurriculumFetchView(APIView):
    permission_classes = [IsAdminUser]
    """
    This class is created to fetch the detail of the curruiculum.
    """
    def get(self, request, pk):
        try:
            data = Curriculum.objects.get(id=pk)
            serializer = CurriculumDetailSerializer(data)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.CURRICULUM_DETAIL_MESSAGE,
                data=serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=CurriculumMessage.CURRICULUM_NOT_FOUND,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)