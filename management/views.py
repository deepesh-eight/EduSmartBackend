from django.db.models import Q
from django.db.models.functions import ExtractMonth
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import StaffUser, TimeTable, TeacherUser, StudentUser
from authentication.permissions import IsInSameSchool, IsStaffUser
from constants import UserLoginMessage, UserResponseMessage, TimeTableMessage, ReportCardMesssage, month_mapping, \
    SalaryMessage, FeeMessage
from management.models import Salary, Fee
from management.serializers import ManagementProfileSerializer, TimeTableSerializer, TimeTableDetailViewSerializer, \
    ExamReportCardSerializer, StudentReportCardSerializer, AddSalarySerializer, SalaryDetailSerializer, \
    SalaryUpdateSerializer, AddFeeSerializer, FeeListSerializer, FeeUpdateSerializer, FeeDetailSerializer, \
    StudentListsSerializer, StudentFilterListSerializer, StudentDetailSerializer
from pagination import CustomPagination
from student.models import ExmaReportCard
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
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        response_data = create_response_data(
            status=status.HTTP_201_CREATED,
            message=UserResponseMessage.USER_DETAIL_MESSAGE,
            data=user_detail.data
        )
        return Response(response_data, status=status.HTTP_201_CREATED)


class ExamTimeTableView(APIView):
    """
    This class is used to fetch exam timetable.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            current_date = timezone.now().date()
            teacher_user = StaffUser.objects.get(user=user, user__school_id=request.user.school_id,
                                                 role="Payroll Management")
            exam_timetable = TimeTable.objects.filter(status=1, school_id=user.school_id).order_by('-id')
            if request.query_params.get('exam') == 'current_exam':
                exam_timetable = exam_timetable.filter(exam_month__gte=current_date.replace(day=1)).order_by('-id')

            if request.query_params.get('exam') == 'post_exam':
                exam_timetable = exam_timetable.filter(exam_month__lt=current_date.replace(day=1)).order_by('-id')

            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(exam_timetable, request)

            serializers = TimeTableSerializer(paginated_queryset, many=True)
            response = {
                'status': status.HTTP_200_OK,
                'count': len(serializers.data),
                'message': TimeTableMessage.TIMETABLE_FETCHED_SUCCESSFULLY,
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
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class ExamTimeTableDetailView(APIView):
    """
    This class is used to fetch detail of the timetable according to the class.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            user = request.user
            teacher_user = StaffUser.objects.get(user=user, user__school_id=request.user.school_id,
                                                 role="Payroll Management")
            exam_timetable = TimeTable.objects.get(id=pk, status=1, school_id=user.school_id)
            serializer = TimeTableDetailViewSerializer(exam_timetable)
            response = create_response_data(
                status=status.HTTP_200_OK,
                message=TimeTableMessage.TIMETABLE_FETCHED_SUCCESSFULLY,
                data=serializer.data
            )
            return Response(response, status=status.HTTP_200_OK)
        except TimeTable.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=TimeTableMessage.TIMETABLE_NOT_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class ExamTimeTableDeleteView(APIView):
    """
    This class is used to delete declared timetable which is added by teacher.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def delete(self,request,pk):
        try:
            user = request.user
            teacher_user = StaffUser.objects.get(user=user, user__school_id=request.user.school_id,
                                                 role="Payroll Management")
            exam_timetable = TimeTable.objects.get(id=pk, status=1, school_id=user.school_id)
            exam_timetable.delete()
            response = create_response_data(
                status=status.HTTP_200_OK,
                message=TimeTableMessage.TIMETABLE_DELETED_SUCCESSFULLY,
                data={}
            )
            return Response(response, status=status.HTTP_200_OK)

        except TimeTable.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=TimeTableMessage.TIMETABLE_NOT_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class ExamReportCardListView(APIView):
    """
    This class is used to fetch report card.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            teacher_user = StaffUser.objects.get(user=user, user__school_id=request.user.school_id,
                                                 role="Payroll Management")
            curriculum = request.query_params.get('curriculum', None)
            class_name = request.query_params.get('class', None)
            section = request.query_params.get('section', None)
            exam_type = request.query_params.get('exam_type', None)
            exam_month = request.query_params.get('exam_month', None)
            exam_year = request.query_params.get('exam_year', None)

            report_card = ExmaReportCard.objects.filter(status=1, school_id=request.user.school_id).order_by('-id')

            if curriculum:
                report_card = report_card.filter(curriculum=curriculum)
            if class_name:
                report_card = report_card.filter(class_name=class_name)
            if section:
                report_card = report_card.filter(class_section=section)
            if exam_type:
                report_card = report_card.filter(exam_type=exam_type)
            if exam_month:
                month_number = month_mapping.get(exam_month)
                report_card = report_card.annotate(month=ExtractMonth('exam_month')).filter(month=month_number)
            if exam_year:
                report_card = report_card.filter(updated_at__year=exam_year)
            if exam_month and exam_year:
                month_number = month_mapping.get(exam_month)
                report_card = report_card.annotate(month=ExtractMonth('exam_month')).filter(month=month_number, updated_at__year=exam_year)
            if curriculum and class_name:
                report_card = report_card.filter(curriculum=curriculum, class_name=class_name)
            if curriculum and class_name and section:
                report_card = report_card.filter(curriculum=curriculum, class_name=class_name, class_section=section)
            if curriculum and class_name and section:
                report_card = report_card.filter(curriculum=curriculum, class_name=class_name, class_section=section)
            if curriculum and class_name and section and exam_type:
                report_card = report_card.filter(curriculum=curriculum, class_name=class_name, class_section=section, exam_type=exam_type)
            if curriculum and class_name and section and exam_type and exam_month:
                month_number = month_mapping.get(exam_month)
                report_card = report_card.annotate(month=ExtractMonth('exam_month')).filter(curriculum=curriculum, class_name=class_name, class_section=section, exam_type=exam_type, month=month_number)
            # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(report_card, request)

            serializer = ExamReportCardSerializer(paginated_queryset, many=True)
            response = {
                'status': status.HTTP_200_OK,
                'count': len(serializer.data),
                'message': ReportCardMesssage.REPORT_CARD_FETCHED_SUCCESSFULLY,
                'data': serializer.data,
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
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class ExamReportCardFilterListView(APIView):
    """
    This class is used to fetch report card according to provided curriculum, class, and section.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            teacher_user = StaffUser.objects.get(user=user, user__school_id=request.user.school_id,
                                                 role="Payroll Management")

            curriculum = request.query_params.get('curriculum')
            class_name = request.query_params.get('class')
            section = request.query_params.get('section')
            exam_type = request.query_params.get('exam_type')
            exam_month = request.query_params.get('exam_month')
            exam_year = request.query_params.get('exam_year')

            if curriculum and class_name and section and exam_type and exam_year:
                report_card = ExmaReportCard.objects.filter(status=1, school_id=request.user.school_id, curriculum=curriculum, class_name=class_name, class_section=section,
                                                            updated_at__year=exam_year, exam_type=exam_type).order_by('-id')
                if exam_month:
                    month_number = month_mapping.get(exam_month)
                    report_card = report_card.annotate(month=ExtractMonth('exam_month')).filter(month=month_number)
                # Paginate the queryset
                paginator = self.pagination_class()
                paginated_queryset = paginator.paginate_queryset(report_card, request)

                serializer = ExamReportCardSerializer(paginated_queryset, many=True)
                response = {
                    'status': status.HTTP_200_OK,
                    'count': len(serializer.data),
                    'message': ReportCardMesssage.REPORT_CARD_FETCHED_SUCCESSFULLY,
                    'data': serializer.data,
                    'pagination': {
                        'page_size': paginator.page_size,
                        'next': paginator.get_next_link(),
                        'previous': paginator.get_previous_link(),
                        'total_pages': paginator.page.paginator.num_pages,
                        'current_page': paginator.page.number,
                    }
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Please provide curriculum, class, section, exam_month, exam_type, and exam_year.",
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class StudentReportCardView(APIView):
    """
    This class is used to fetch report card according ot provided student roll_no.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            current_date = timezone.now().date()
            teacher_user = StaffUser.objects.get(user=user, user__school_id=request.user.school_id,
                                                 role="Payroll Management")
            student_name = request.query_params.get('student_name')
            curriculum = request.query_params.get('curriculum', None)
            class_name = request.query_params.get('class', None)
            section = request.query_params.get('section', None)
            exam_type = request.query_params.get('exam_type', None)
            exam_month = request.query_params.get('exam_month', None)
            exam_year = request.query_params.get('exam_year', None)
            report_card = ExmaReportCard.objects.filter(status=1, school_id=request.user.school_id)
            if student_name:
                report_card = report_card.filter(student_name=student_name, updated_at__year=current_date.year)

            if student_name and curriculum and class_name and section and exam_type and exam_year:
                month_number = month_mapping.get(exam_month)
                report_card = report_card.annotate(month=ExtractMonth('exam_month')).filter(student_name=student_name, curriculum=curriculum, class_name=class_name, class_section=section,
                                                            updated_at__year=exam_year, exam_type=exam_type, month=month_number)

            serializer = StudentReportCardSerializer(report_card, many=True)
            response = create_response_data(
                status=status.HTTP_200_OK,
                message=ReportCardMesssage.REPORT_CARD_FETCHED_SUCCESSFULLY,
                data=serializer.data
            )
            return Response(response, status=status.HTTP_200_OK)

        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXISTS,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={},
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class AddSalaryView(APIView):
    """
    This class is used to add salary details of the staff it can be non-teaching or teaching.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def post(self, request):
        try:
            serializer = AddSalarySerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(school_id=request.user.school_id)
                response = create_response_data(
                    status=status.HTTP_201_CREATED,
                    message=SalaryMessage.SALARY_ADDED_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class SalaryDetailView(APIView):
    """
    This class is used to fetch detail of the salary detail.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            data = Salary.objects.get(id=pk, school_id=request.user.school_id)
            serilizer = SalaryDetailSerializer(data)
            response = create_response_data(
                        status=status.HTTP_201_CREATED,
                        message=SalaryMessage.SALARY_DETAIL_FETCH_SUCCESSFULLY,
                        data=serilizer.data
                    )
            return Response(response, status=status.HTTP_201_CREATED)
        except Salary.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=SalaryMessage.SALARY_DETAIL_NOT_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class SalaryUpdateView(APIView):
    """
    This class is used to update the salary related data.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def patch(self, request, pk):
        try:
            data = Salary.objects.get(id=pk, school_id=request.user.school_id)
            serializer = SalaryUpdateSerializer(data, data=request.data, partial=True,
                                                          context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=SalaryMessage.SALARY_UPDATED_SUCCESSFULLY,
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

        except Salary.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=SalaryMessage.SALARY_DETAIL_NOT_EXIST,
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


class AddFeeView(APIView):
    """
    This class is used to add fee details of the student.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def post(self, request):
        try:
            serializer = AddFeeSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                serializer.save(school_id=request.user.school_id)
                response = create_response_data(
                    status=status.HTTP_201_CREATED,
                    message=FeeMessage.FEE_ADDED_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response, status=status.HTTP_201_CREATED)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class FeeListView(APIView):
    """
    This class is used to fetch list of salary list of all student's.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            search = self.request.query_params.get('search', None)

            data = Fee.objects.filter(school_id=request.user.school_id).order_by('-id')
            if search:
                data = data.filter(Q(curriculum__icontains=search) | Q(class_name__icontains=search) | Q(payment_type__icontains=search)
                                   | Q(total_fee__icontains=search) | Q(total_fee__icontains=search))

                # Paginate the queryset
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(data, request)

            serializer = FeeListSerializer(paginated_queryset, many=True)
            response = {
                'status': status.HTTP_201_CREATED,
                'count': len(serializer.data),
                'message': FeeMessage.FEE_DETAIL_FETCH_SUCCESSFULLY,
                'data': serializer.data,
                'pagination': {
                    'page_size': paginator.page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': paginator.page.number,
                }
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class FeeUpdateView(APIView):
    """
    This class is used to update detail of the student fee.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def patch(self, request, pk):
        try:
            data = Fee.objects.get(id=pk, school_id=request.user.school_id)
            serializer = FeeUpdateSerializer(data, data=request.data, partial=True,
                                                          context={'request': request})
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=FeeMessage.FEE_UPDATED_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response_data = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data={}
                )
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        except Fee.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=FeeMessage.FEE_DETAIL_NOT_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class FeeDetailView(APIView):
    """
    This class is used to fetch the detail of student fee.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            data = Fee.objects.get(id=pk, school_id=request.user.school_id)
            serializer = FeeDetailSerializer(data)
            response = create_response_data(
                status=status.HTTP_200_OK,
                message=FeeMessage.FEE_DETAIL_FETCH_SUCCESSFULLY,
                data=serializer.data
            )
            return Response(response, status=status.HTTP_200_OK)

        except Fee.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=FeeMessage.FEE_DETAIL_NOT_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class StudentList(APIView):
    """
    This class is used to fetch total list of the student in every class.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            data = TeacherUser.objects.filter(user__school_id=request.user.school_id, user__is_active=True)
            search = self.request.query_params.get('search', None)
            if search:
                data = data.filter(class_subject_section_details__contains=[{'class': search}])

            paginator = self.pagination_class()
            paginator_queryset = paginator.paginate_queryset(data, request)

            serializer = StudentListsSerializer(paginator_queryset, many=True)
            filtered_data = [entry for entry in serializer.data if entry]
            response_data = {
                'status': status.HTTP_201_CREATED,
                'count': len(serializer.data),
                'message': UserResponseMessage.USER_LIST_MESSAGE,
                'data': filtered_data,
                'pagination': {
                    'page_size': paginator.page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': paginator.page.number,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class StudentFilterList(APIView):
    """
    This class is used to fetch list of the student according to the classes.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            data = StudentUser.objects.filter(user__school_id=request.user.school_id, user__is_active=True)
            curriculum = self.request.query_params.get('curriculum', None)
            class_name = self.request.query_params.get('class', None)
            section = self.request.query_params.get('section', None)
            search  = self.request.query_params.get('search', None)
            if curriculum and class_name and section:
                data = data.filter(curriculum=curriculum, class_enrolled=class_name, section=section)
                if search:
                    data = data.filter(name__icontains=search)
                paginator = self.pagination_class()
                paginator_queryset = paginator.paginate_queryset(data, request)

                serializer = StudentFilterListSerializer(paginator_queryset, many=True)
                response_data = {
                    'status': status.HTTP_201_CREATED,
                    'count': len(serializer.data),
                    'message': UserResponseMessage.USER_LIST_MESSAGE,
                    'data': serializer.data,
                    'pagination': {
                        'page_size': paginator.page_size,
                        'next': paginator.get_next_link(),
                        'previous': paginator.get_previous_link(),
                        'total_pages': paginator.page.paginator.num_pages,
                        'current_page': paginator.page.number,
                    }
                }
                return Response(response_data, status=status.HTTP_201_CREATED)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Please provide curriculum, class, and section.",
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class StudentFeeDetail(APIView):
    """
    This class is used to fetch detail of the student fee.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, reqeuest, pk):
        try:
            student_data = StudentUser.objects.get(id=pk)
            serializer = StudentDetailSerializer(student_data)
            response = create_response_data(
                status=status.HTTP_200_OK,
                message=FeeMessage.STUDENT_FEE_DETAIL_FETCH_SUCCESSFULLY,
                data=serializer.data
            )
            return Response(response, status=status.HTTP_200_OK)
        except StudentUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=FeeMessage.FEE_DETAIL_NOT_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class TeacherList(APIView):
    """
    This class is used to fetch list of the teacher's.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            data = TeacherUser.objects.filter(user__school_id=request.user.school_id, user__is_active=True)
            paginator = self.pagination_class()
            paginator_queryset = paginator.paginate_queryset(data, request)

            serializer = StudentListsSerializer(paginator_queryset, many=True)
            filtered_data = [entry for entry in serializer.data if entry]
            response_data = {
                'status': status.HTTP_201_CREATED,
                'count': len(serializer.data),
                'message': UserResponseMessage.USER_LIST_MESSAGE,
                'data': filtered_data,
                'pagination': {
                    'page_size': paginator.page_size,
                    'next': paginator.get_next_link(),
                    'previous': paginator.get_previous_link(),
                    'total_pages': paginator.page.paginator.num_pages,
                    'current_page': paginator.page.number,
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=e.args[0],
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)