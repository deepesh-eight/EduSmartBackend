from django.urls import path
from .views import RouteListView, RouteCreateView

urlpatterns = [
    path('routes/', RouteListView.as_view(), name='route-list'),
    path('routes/create/', RouteCreateView.as_view(), name='route-create'),
]