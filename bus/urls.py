from django.urls import path
from .views import RouteListView, RouteCreateView, CreateBusView, BusListView, BusDeleteView, BusDetailView

urlpatterns = [
    path('routes/', RouteListView.as_view(), name='route-list'),
    path('routes/create/', RouteCreateView.as_view(), name='route-create'),
    path('bus/create/', CreateBusView.as_view(), name='bus-create'),
    path('bus-list/', BusListView.as_view(), name='bus-list'),
    path('bus/delete/<int:pk>/', BusDeleteView.as_view(), name='bus-delete'),
    path('bus/detail/<int:pk>/', BusDetailView.as_view(), name='bus-detail'),
]