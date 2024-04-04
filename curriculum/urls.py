from django.urls import path
from .views import *

urlpatterns = [
        path('create/', CurriculumCreateView.as_view(), name='curriculom_create'),
        path('fetch/list/', CurriculumlistView.as_view(), name='fetch_curriculom_listl'),
        ]