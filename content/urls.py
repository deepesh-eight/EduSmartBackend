from django.urls import path
from .views import ContentCreateView, ContentListView

urlpatterns = [
    path('create/', ContentCreateView.as_view(), name='content-create'),
    path('get-all-data/', ContentListView.as_view(), name='get-all-content-data'),
]