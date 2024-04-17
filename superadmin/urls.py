from django.urls import path
from .views import *

urlpatterns = [
        path('school/create/', SchoolCreateView.as_view(), name='student_user_create'),
]