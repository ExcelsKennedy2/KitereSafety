from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('reports/', views.reports_list, name='reports_list'),
    path('users/', views.users_management, name='users'),
]