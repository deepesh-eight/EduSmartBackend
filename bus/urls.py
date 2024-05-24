from django.urls import path
from .views import RouteCreateView, CreateBusView, BusListView, BusDeleteView, BusDetailView, \
    BusRouteListView, BusRouteDetailView, BusRouteDeleteView, BusDetailUpdateView

urlpatterns = [
    # Bus API
    path('bus/create/', CreateBusView.as_view(), name='bus-create'),
    path('bus-list/', BusListView.as_view(), name='bus-list'),
    path('bus/delete/<int:pk>/', BusDeleteView.as_view(), name='bus-delete'),
    path('bus/detail/<int:pk>/', BusDetailView.as_view(), name='bus-detail'),
    path('update/<int:pk>/', BusDetailUpdateView.as_view(), name='bus-update'),

    # Bus route API
    path('routes/create/', RouteCreateView.as_view(), name='route-create'),
    path('route/list/', BusRouteListView.as_view(), name='bus-route-list'),
    path('route/detail/<int:pk>/', BusRouteDetailView.as_view(), name='bus-route-detail'),
    path('route/delete/<int:pk>/', BusRouteDeleteView.as_view(), name='bus-route-delete'),
]