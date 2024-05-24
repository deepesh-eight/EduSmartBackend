from django.urls import path
from .views import RouteCreateView, CreateBusView, BusListView, BusDeleteView, BusDetailView, \
    BusRouteListView, BusRouteDetailView

urlpatterns = [
    # Bus API
    path('bus/create/', CreateBusView.as_view(), name='bus-create'),
    path('bus-list/', BusListView.as_view(), name='bus-list'),
    path('bus/delete/<int:pk>/', BusDeleteView.as_view(), name='bus-delete'),
    path('bus/detail/<int:pk>/', BusDetailView.as_view(), name='bus-detail'),

    # Bus route API
    path('routes/create/', RouteCreateView.as_view(), name='route-create'),
    path('route/list/', BusRouteListView.as_view(), name='bus-route-list'),
    path('route/detail/<int:pk>/', BusRouteDetailView.as_view(), name='bus-route-detail'),
]