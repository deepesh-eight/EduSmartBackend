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
    This class is used to fetch details of management.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            # Ensure user is authenticated and has the correct school_id
            staff = StaffUser.objects.get(user=user, user__school_id=user.school_id)

            # Set a breakpoint for debugging if needed
            # breakpoint()

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                user_detail = ManagementProfileSerializer(staff)

                response_data = create_response_data(
                    status=status.HTTP_200_OK,
                    message=UserResponseMessage.USER_DETAIL_MESSAGE,
                    data=user_detail.data
                )
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class ExamTimeTableView(APIView):
    """
    This class is used to fetch exam timetable.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=request.user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                current_date = timezone.now().date()
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
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class ExamTimeTableDetailView(APIView):
    """
    This class is used to fetch details of the timetable according to the class.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                teacher_user = StaffUser.objects.get(
                    user=user,
                    user__school_id=user.school_id,
                    role="Payroll Management"
                )

                # Fetch the timetable
                exam_timetable = TimeTable.objects.get(id=pk, status=1, school_id=user.school_id)
                serializer = TimeTableDetailViewSerializer(exam_timetable)
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=TimeTableMessage.TIMETABLE_FETCHED_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

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
                message=UserLoginMessage.USER_DOES_NOT_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
                data={}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)



class ExamTimeTableDeleteView(APIView):
    """
    This class is used to delete a declared timetable which is added by a teacher.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def delete(self, request, pk):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                teacher_user = StaffUser.objects.get(
                    user=user,
                    user__school_id=user.school_id,
                    role="Payroll Management"
                )

                # Fetch and delete the timetable
                exam_timetable = TimeTable.objects.get(id=pk, status=1, school_id=user.school_id)
                exam_timetable.delete()

                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=TimeTableMessage.TIMETABLE_DELETED_SUCCESSFULLY,
                    data={}
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

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
                message=UserLoginMessage.USER_DOES_NOT_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
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
            staff = StaffUser.objects.get(user=user, user__school_id=user.school_id)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                teacher_user = StaffUser.objects.get(
                    user=user,
                    user__school_id=user.school_id,
                    role="Payroll Management"
                )

                # Get query parameters
                curriculum = request.query_params.get('curriculum', None)
                class_name = request.query_params.get('class', None)
                section = request.query_params.get('section', None)
                exam_type = request.query_params.get('exam_type', None)
                exam_month = request.query_params.get('exam_month', None)
                exam_year = request.query_params.get('exam_year', None)

                # Initial report card query
                report_card = ExmaReportCard.objects.filter(status=1, school_id=user.school_id).order_by('-id')

                # Apply filters based on query parameters
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
                    report_card = report_card.annotate(month=ExtractMonth('exam_month')).filter(
                        month=month_number, updated_at__year=exam_year
                    )
                if curriculum and class_name:
                    report_card = report_card.filter(curriculum=curriculum, class_name=class_name)
                if curriculum and class_name and section:
                    report_card = report_card.filter(curriculum=curriculum, class_name=class_name, class_section=section)
                if curriculum and class_name and section and exam_type:
                    report_card = report_card.filter(
                        curriculum=curriculum, class_name=class_name, class_section=section, exam_type=exam_type
                    )
                if curriculum and class_name and section and exam_type and exam_month:
                    month_number = month_mapping.get(exam_month)
                    report_card = report_card.annotate(month=ExtractMonth('exam_month')).filter(
                        curriculum=curriculum, class_name=class_name, class_section=section,
                        exam_type=exam_type, month=month_number
                    )

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
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXIST,
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response_data = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
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
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                teacher_user = StaffUser.objects.get(user=user, user__school_id=request.user.school_id, role="Payroll Management")

            curriculum = request.query_params.get('curriculum')
            class_name = request.query_params.get('class')
            section = request.query_params.get('section')
            exam_type = request.query_params.get('exam_type')
            exam_month = request.query_params.get('exam_month')
            exam_year = request.query_params.get('exam_year')

            if curriculum and class_name and section and exam_type and exam_year:
                report_card = ExmaReportCard.objects.filter(
                    status=1,
                    school_id=request.user.school_id,
                    curriculum=curriculum,
                    class_name=class_name,
                    class_section=section,
                    updated_at__year=exam_year,
                    exam_type=exam_type
                ).order_by('-id')

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
    This class is used to fetch report card according to the provided student roll_no.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                current_date = timezone.now().date()

                student_name = request.query_params.get('student_name')
                curriculum = request.query_params.get('curriculum', None)
                class_name = request.query_params.get('class_name', None)
                section = request.query_params.get('section', None)
                exam_type = request.query_params.get('exam_type', None)
                exam_month = request.query_params.get('exam_month', None)
                exam_year = request.query_params.get('exam_year', None)

                report_card = ExmaReportCard.objects.filter(status=1, school_id=request.user.school_id)

                if student_name and curriculum and class_name and section and exam_type and exam_year:
                    month_number = month_mapping.get(exam_month)
                    report_card = report_card.annotate(month=ExtractMonth('exam_month')).filter(
                        student_name=student_name,
                        curriculum=curriculum,
                        class_name=class_name,
                        class_section=section,
                        updated_at__year=exam_year,
                        exam_type=exam_type,
                        month=month_number
                    )
                elif student_name:
                    report_card = report_card.filter(
                        student_name=student_name,
                        updated_at__year=current_date.year
                    )

                serializer = StudentReportCardSerializer(report_card, many=True)
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=ReportCardMesssage.REPORT_CARD_FETCHED_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response, status=status.HTTP_200_OK)

            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
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



class AddSalaryView(APIView):
    """
    This class is used to add salary details of the staff; it can be non-teaching or teaching.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def post(self, request):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
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
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
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
    This class is used to fetch details of the salary.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                data = Salary.objects.get(id=pk, school_id=request.user.school_id)
                serializer = SalaryDetailSerializer(data)
                response = create_response_data(
                    status=status.HTTP_200_OK,  # Changed to 200 OK for fetching details
                    message=SalaryMessage.SALARY_DETAIL_FETCH_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response, status=status.HTTP_200_OK)  # Changed to 200 OK for fetching details
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
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
            else:
                response_data = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
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
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
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
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
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
    This class is used to fetch the list of fee details for all students.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
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
                    'status': status.HTTP_200_OK,
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
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
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



class FeeUpdateView(APIView):
    """
    This class is used to update details of the student's fee.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def patch(self, request, pk):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
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
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

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
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                data = Fee.objects.get(id=pk, school_id=request.user.school_id)
                serializer = FeeDetailSerializer(data)
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=FeeMessage.FEE_DETAIL_FETCH_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

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
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
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
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
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


class StudentFilterList(APIView):
    """
    This class is used to fetch a list of students according to the classes.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                data = StudentUser.objects.filter(user__school_id=request.user.school_id, user__is_active=True)
                curriculum = self.request.query_params.get('curriculum', None)
                class_name = self.request.query_params.get('class', None)
                section = self.request.query_params.get('section', None)
                search = self.request.query_params.get('search', None)

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
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
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
    This class is used to fetch the detail of the student fee.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                student_data = StudentUser.objects.get(id=pk)
                serializer = StudentDetailSerializer(student_data)
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=FeeMessage.STUDENT_FEE_DETAIL_FETCH_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserResponseMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
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
    This class is used to fetch a list of teachers.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                data = TeacherUser.objects.filter(
                    user__school_id=request.user.school_id,
                    user__is_active=True
                ).order_by('id')

                paginator = self.pagination_class()
                paginator_queryset = paginator.paginate_queryset(data, request)

                serializer = TeacherListsSerializer(paginator_queryset, many=True)
                filtered_data = [entry for entry in serializer.data if entry]

                response_data = {
                    'status': status.HTTP_200_OK,
                    'count': len(filtered_data),
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
                return Response(response_data, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserResponseMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)




class TeacherSalaryDetailView(APIView):
    """
    This class is used to fetch the detail of a teacher's salary.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request, pk):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                data = TeacherUser.objects.get(id=pk, user__school_id=request.user.school_id)
                serializer = TeacherFeeDetailSerializer(data)
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=FeeMessage.FEE_DETAIL_FETCH_SUCCESSFULLY,
                    data=serializer.data
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserResponseMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except TeacherUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_NOT_FOUND,
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


class StaffList(APIView):
    """
    This class is used to fetch details of the staff.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]
    pagination_class = CustomPagination

    def get(self, request):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role == "Payroll Management" or staff.role == "Management") and user.user_type == "non-teaching":
                data = StaffUser.objects.filter(user__school_id=request.user.school_id, user__is_active=True).order_by('-id')
                paginator = self.pagination_class()
                paginator_queryset = paginator.paginate_queryset(data, request)

                serializer = StaffListsSerializer(paginator_queryset, many=True)
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
                    message=UserResponseMessage.USER_DOES_NOT_EXIST,
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


class TeacherSalaryUpdateView(APIView):
    """
    This class is used to update the details of the teacher's fee detail.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def patch(self, request, pk):
        try:
            teacher_user = TeacherUser.objects.get(id=pk)
            staff = StaffUser.objects.get(user=request.user)

            # Check role and user type
            if (
                    staff.role == "Payroll Management" or staff.role == "Management") and request.user.user_type == "non-teaching":
                data = Salary.objects.get(name=teacher_user.user.id, school_id=request.user.school_id)
                serializer = TeacherUserSalaryUpdateSerializer(data, data=request.data, partial=True)

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
            else:
                response_data = create_response_data(
                    status=status.HTTP_403_FORBIDDEN,
                    message=UserResponseMessage.USER_DOES_NOT_HAVE_PERMISSION,
                    data={}
                )
                return Response(response_data, status=status.HTTP_403_FORBIDDEN)

        except TeacherUser.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_NOT_FOUND,
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


class StaffSalaryUpdateView(APIView):
    """
    This class is used to update the details of the non-teaching staff fee detail.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def patch(self, request, pk):
        try:
            staff_user = StaffUser.objects.get(id=pk)
            staff = StaffUser.objects.get(user=request.user)

            # Check role and user type
            if (
                    staff.role == "Payroll Management" or staff.role == "Management") and request.user.user_type == "non-teaching":
                data = Salary.objects.get(name=staff_user.user.id, school_id=request.user.school_id)
                serializer = TeacherUserSalaryUpdateSerializer(data, data=request.data, partial=True)

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
            else:
                response_data = create_response_data(
                    status=status.HTTP_403_FORBIDDEN,
                    message=UserResponseMessage.USER_DOES_NOT_HAVE_PERMISSION,
                    data={}
                )
                return Response(response_data, status=status.HTTP_403_FORBIDDEN)

        except StaffUser.DoesNotExist:
            response_data = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_NOT_FOUND,
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


class UserListView(APIView):
    """
    This class is used to fetch the list of teaching and non-teaching staff.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request):
        try:
            user = request.user
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if (staff.role in ["Payroll Management", "Management"]) and user.user_type == "non-teaching":
                data = User.objects.filter(
                    school_id=request.user.school_id,
                    is_active=True,
                    user_type__in=['teacher', 'non-teaching']
                ).values('id', 'name')

                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=UserResponseMessage.USER_LIST_MESSAGE,
                    data=list(data)
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserResponseMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_NOT_FOUND,
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


class StaffSalaryDetailView(APIView):
    """
    This class is used to fetch the detail of non-teaching-staff.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def get(self, request, pk):
        user = request.user

        try:
            staff = StaffUser.objects.get(user=user)

            # Check role and user type
            if not (staff.role in ["Payroll Management", "Management"] and user.user_type == "non-teaching"):
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            # Fetch staff details
            data = StaffUser.objects.get(id=pk, user__school_id=request.user.school_id)
            serializer = StaffFeeDetailSerializer(data)
            response = create_response_data(
                status=status.HTTP_200_OK,
                message=FeeMessage.FEE_DETAIL_FETCH_SUCCESSFULLY,
                data=serializer.data
            )
            return Response(response, status=status.HTTP_200_OK)

        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_NOT_FOUND,
                data={}
            )
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class TeacherAttendanceUpdateView(APIView):
    """
    This class is used to update the detail of the teacher attendance.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def patch(self, request, pk):
        user = request.user
        try:
            staff = StaffUser.objects.get(user=user)
            if not (staff.role in ["Payroll Management", "Management"] and user.user_type == "non-teaching"):
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            teacher = TeacherUser.objects.get(id=pk, user__school_id=request.user.school_id)
            date = request.data.get('date')
            mark_attendence = request.data.get('mark_attendence')
            if not date or not mark_attendence:
                response= (
                    create_response_data(
                        status=status.HTTP_400_BAD_REQUEST,
                        message="Date and mark_attendence are required.",
                        data={}
                    )
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            try:
                attendance_record = TeacherAttendence.objects.get(teacher=teacher, date=date)
            except TeacherAttendence.DoesNotExist:
                response= (
                    create_response_data(
                        status=status.HTTP_404_NOT_FOUND,
                        message="Attendance record not found for the specified date.",
                        data={}
                    )
                )
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            serializer = TeacherAttendanceUpdateSerializer(attendance_record, data={'mark_attendence': mark_attendence}, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=AttendenceMarkedMessage.ATTENDANCE_UPDATED_SUCCESSFULLY,
                    data={}
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except TeacherUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXISTS,
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


class StaffAttendanceUpdateView(APIView):
    """
    This class is used to update the detail of the staff attendance.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def patch(self, request, pk):
        user = request.user

        try:
            # Check if the user has the appropriate role and user type
            staff = StaffUser.objects.get(user=user)
            if not (staff.role in ["Payroll Management", "Management"] and user.user_type == "non-teaching"):
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            # Proceed with updating attendance
            staff_member = StaffUser.objects.get(id=pk, user__school_id=request.user.school_id)
            date = request.data.get('date')
            mark_attendence = request.data.get('mark_attendence')

            if not date or not mark_attendence:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Date and mark_attendence are required.",
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

            try:
                attendance_record = StaffAttendence.objects.get(staff=staff_member, date=date)
            except StaffAttendence.DoesNotExist:
                response = create_response_data(
                    status=status.HTTP_404_NOT_FOUND,
                    message="Attendance record not found for the specified date.",
                    data={}
                )
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            serializer = StaffAttendanceUpdateSerializer(attendance_record, data={'mark_attendence': mark_attendence}, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=AttendenceMarkedMessage.ATTENDANCE_UPDATED_SUCCESSFULLY,
                    data={}
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)

        except StaffUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_404_NOT_FOUND,
                message=UserResponseMessage.USER_NOT_FOUND,
                data={}
            )
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=str(e),
                data={}
            )
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class StudentAttendanceUpdateView(APIView):
    """
    This class is used to update the detail of the student attendance.
    """
    permission_classes = [IsStaffUser, IsInSameSchool]

    def patch(self, request, pk):
        user = request.user
        try:
            staff = StaffUser.objects.get(user=user)
            if not (staff.role in ["Payroll Management", "Management"] and user.user_type == "non-teaching"):
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=UserLoginMessage.USER_DOES_NOT_EXIST,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            student = StudentUser.objects.get(id=pk, user__school_id=request.user.school_id)
            date = request.data.get('date')
            mark_attendence = request.data.get('mark_attendence')
            if not date or not mark_attendence:
                response= (
                    create_response_data(
                        status=status.HTTP_400_BAD_REQUEST,
                        message="Date and mark_attendence are required.",
                        data={}
                    )
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
            try:
                attendance_record = StudentAttendence.objects.get(student=student, date=date)
            except StudentAttendence.DoesNotExist:
                response= (
                    create_response_data(
                        status=status.HTTP_404_NOT_FOUND,
                        message="Attendance record not found for the specified date.",
                        data={}
                    )
                )
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            serializer = StudentAttendanceUpdateSerializer(attendance_record, data={'mark_attendence': mark_attendence}, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                response = create_response_data(
                    status=status.HTTP_200_OK,
                    message=AttendenceMarkedMessage.ATTENDANCE_UPDATED_SUCCESSFULLY,
                    data={}
                )
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = create_response_data(
                    status=status.HTTP_400_BAD_REQUEST,
                    message=serializer.errors,
                    data={}
                )
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        except StudentUser.DoesNotExist:
            response = create_response_data(
                status=status.HTTP_400_BAD_REQUEST,
                message=UserLoginMessage.USER_DOES_NOT_EXISTS,
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
