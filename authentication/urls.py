from django.urls import path

from . views import *

urlpatterns = [
        path('users/create/', UserCreateView.as_view(), name='user_create'),
        path('users/login/', LoginView.as_view(), name='user_login'),
        path('fetch/user/detail/<int:pk>/', FetchUserDetailView.as_view(), name='fetch_user_detail'),
        path('users/list/', UsersList.as_view(), name='users_list'),
        path('user/delete/<int:pk>/', UserDeleteView.as_view(), name='user_delete'),
        path('user/update-profile/', UserUpdateProfileView.as_view(), name='update_profile'),
]