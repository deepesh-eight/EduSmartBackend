from django.urls import path
from .views import *

urlpatterns = [
        path('create/', CurriculumCreateView.as_view(), name='curriculom_create'),
        path('upload/', CurriculumUploadView.as_view(), name='curriculom_upload'),
        path('fetch/list/', CurriculumlistView.as_view(), name='fetch_curriculom_list'),
        path('fetch/curriculum/detail/<int:pk>/', CurriculumFetchView.as_view(), name='fetch_curriculom'),
        path('delete/curriculum/<int:pk>/', CurriculumDeleteView.as_view(), name='delete_curriculom'),
        ]