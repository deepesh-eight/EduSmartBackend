from django.urls import path
from .views import *

urlpatterns = [
        path('school/create/', SchoolCreateView.as_view(), name='school_create'),
        path('school/profile/<int:pk>/', SchoolProfileView.as_view(), name='fetch_school_profile'),
        path('school/profile/update/<int:pk>/', SchoolProfileUpdateView.as_view(), name='schedule_update'),
        path('school/profile/', SchoolAdminProfileView.as_view(), name='schedule_profile'),
]