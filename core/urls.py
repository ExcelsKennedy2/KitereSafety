from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    # path('services/', views.services, name='services'),
    # path('about/', views.about, name='about'),
    # path('terms/', views.terms, name='terms'),
    # path('privacy/', views.privacy, name='privacy'),
    # path('contact/', views.contact, name='contact'),
]