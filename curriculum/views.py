import json

from rest_framework import status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from EduSmart import settings
from authentication.permissions import IsAdminUser, IsInSameSchool
from constants import CurriculumMessage
from curriculum.models import Curriculum, CurriculumPDF
from curriculum.serializers import CurriculumSerializer, CurriculumDetailSerializer, CurriculumUploadSerializer, \
    CurriculumListerializer, SuperAdminCurriculumClassList, CurriculumDetailUpdateSerializer
from pagination import CustomPagination
from superadmin.models import CurricullumList, Subjects
from superadmin.serializers import SuperAdminCurriculumSubjectList, SuperAdminCurriculumOptionalSubjectList
from utils import create_response_data, create_response_list_data


# Create your views here.


class CurriculumCreateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is used to create curriculum.
    """
    def post(self, request):
        try:
            # primary_subject = request.data.get("primary_subject")
            # optional_subject = request.data.get("optional_subject")
            # primary_subject_str = json.loads(primary_subject)
            # optional_subject_str = json.loads(optional_subject)
            # data = {
            #     "curriculum_name": request.data.get("curriculum_name"),
            #     "select_class": request.data.get("select_class"),
            #     "primary_subject": primary_subject_str,
            #     "optional_subject": optional_subject_str,
            #     "syllabus": request.data.get("syllabus"),
            #     "discription": request.data.get("discription")
            # }
            serializer = CurriculumSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(school_id=request.user.school_id)
                response = create_response_data(
                    status=status.HTTP_201_CREATED,
                    message=CurriculumMessage.CURRICULUM_CREATED_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data=serializer.errors
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except ValidationError as er:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(er.detail.get('non_field_errors')[0]),
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class CurriculumUploadView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
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
                academic_session=academic_session, exam_board=exam_board, class_name=class_name, section=section, subject_name_code=subject_name_code, school_id=request.user.school_id)
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
    permission_classes = [IsAdminUser, IsInSameSchool]
    pagination_class = CustomPagination
    """
    This class is created to fetch the list of the curriculum.
    """
    def get(self,request):
        queryset = Curriculum.objects.filter(school_id=request.user.school_id).order_by('-id')
        # for curriculum in queryset:
        #     if not curriculum.curriculum_name:
        #         querset1 = CurriculumPDF.objects.all()
        #         for pdf_data in querset1:
        #             curriculum.curriculum_name = f"{settings.base_url}{settings.MEDIA_URL}{pdf_data.curriculum_pdf_file}"
        #             curriculum.save()
        if request.query_params:
            academic_session = request.query_params.get('academic_session', None)
            class_name = request.query_params.get('class_name', None)
            if academic_session:
                queryset = queryset.filter(academic_session__icontains=academic_session)
            if class_name:
                queryset = queryset.filter(select_class__icontains=class_name)
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = CurriculumListerializer(paginated_queryset, many=True)
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
        serializer = CurriculumListerializer(queryset, many=True)
        response = create_response_list_data(
            status=status.HTTP_200_OK,
            count=len(serializer.data),
            message=CurriculumMessage.CURRICULUM_LIST_MESSAGE,
            data=serializer.data,
        )
        return Response(response, status=status.HTTP_200_OK)


class CurriculumDeleteView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is created to delete the curriculum.
    """
    def delete(self, request, pk):
        try:
            curriculum_detail = Curriculum.objects.get(id=pk, school_id=request.user.school_id)
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
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is created to fetch the detail of the curruiculum.
    """
    def get(self, request, pk):
        try:
            data = Curriculum.objects.get(id=pk, school_id=request.user.school_id)
            # if not data.curriculum_name:
            #     querset1 = CurriculumPDF.objects.get(curriculum=data.id)
            #     data.curriculum_name = f"{settings.base_url}{settings.MEDIA_URL}{querset1.curriculum_pdf_file}"
            #     data.save()
            serializer = CurriculumDetailSerializer(data)
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.CURRICULUM_DETAIL_MESSAGE,
                data=serializer.data
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Curriculum.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=CurriculumMessage.CURRICULUM_NOT_FOUND,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=CurriculumMessage.CURRICULUM_NOT_FOUND,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class CurriculumUpdateView(APIView):
    permission_classes = [IsAdminUser, IsInSameSchool]
    """
    This class is created to update the detail of the curruiculum.
    """

    def patch(self, request, pk):
        try:
            data = Curriculum.objects.get(id=pk)
            serializer = CurriculumDetailUpdateSerializer(data, data=request.data, partial=True, context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=CurriculumMessage.CURRICULUM_UPDATED_MESSAGE,
                    data=serializer.data
                )
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response_data = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data={}
                )
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        except Curriculum.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=CurriculumMessage.CURRICULUM_NOT_FOUND,
                data={}
            )
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class CurriculumListView(APIView):
    """
    This class is used to fetch the list of the curriculum which is added by superadmin.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            data = CurricullumList.objects.values_list('curriculum_name', flat=True).distinct()
            curriculum = list(data)
            curriculum_list = {
                "curriculum_name": curriculum
            }
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.CURRICULUM_LIST_MESSAGE,
                data=curriculum_list
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class CurriculumClassListView(APIView):
    """
    This class is used to fetch the list of the classes which is added by superadmin.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            curriculum = request.query_params.get("curriculum_name")
            data = CurricullumList.objects.filter(curriculum_name=curriculum)
            serializer = SuperAdminCurriculumClassList(data, many=True)
            class_names = [item['class_name'] for item in serializer.data]
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.CLASSES_LIST_MESSAGE,
                data=class_names
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class CurriculumsubjectListView(APIView):
    """
    This class is used to fetch the list of the subject which is added by superadmin according to curriculum.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            curriculum = request.query_params.get("curriculum_name")
            classes = request.query_params.get("class_name")
            curriculum_id = CurricullumList.objects.get(curriculum_name=curriculum, class_name=classes)
            subject = Subjects.objects.filter(curriculum_id=curriculum_id.id)
            serializer = SuperAdminCurriculumSubjectList(subject, many=True)
            subjects = [item['primary_subject'] for item in serializer.data]
            subject_list = [subjects.title() for subjects in subjects]
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.SUBJECT_LIST_MESSAGE,
                data=set(subject_list)
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class CurriculumOptionalsubjectListView(APIView):
    """
    This class is used to fetch the list of the optional subject which is added by superadmin according to curriculum.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            curriculum = request.query_params.get("curriculum_name")
            classes = request.query_params.get("class_name")
            curriculum_id = CurricullumList.objects.get(curriculum_name=curriculum, class_name=classes)
            subject = Subjects.objects.filter(curriculum_id=curriculum_id.id)
            serializer = SuperAdminCurriculumOptionalSubjectList(subject, many=True)
            optional_subj = [item['optional_subject'] for item in serializer.data]
            subject_list = [subjects.title() for subjects in optional_subj]
            response_data = create_response_data(
                status=status.HTTP_200_OK,
                message=CurriculumMessage.SUBJECT_LIST_MESSAGE,
                data=set(subject_list)
            )
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)