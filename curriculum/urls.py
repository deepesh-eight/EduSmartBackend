from django.urls import path
from .views import *

urlpatterns = [
        path('create/', CurriculumCreateView.as_view(), name='curriculom_create'),
        path('upload/', CurriculumUploadView.as_view(), name='curriculom_upload'),
        path('fetch/list/', CurriculumlistView.as_view(), name='fetch_curriculom_list'),
        path('fetch/curriculum/detail/<int:pk>/', CurriculumFetchView.as_view(), name='fetch_curriculom'),
        path('delete/curriculum/<int:pk>/', CurriculumDeleteView.as_view(), name='delete_curriculom'),

        # Super admin curriculum list
        path('curriculum/list/', CurriculumListView.as_view(), name='curriculum_list'),
        path('class/list/', CurriculumClassListView.as_view(), name='curriculum_class_list'),
        path('subject/list/', CurriculumsubjectListView.as_view(), name='curriculum_subject_list'),
        path('optional/subject/list/', CurriculumOptionalsubjectListView.as_view(), name='curriculum_optional_subject_list'),
        ]