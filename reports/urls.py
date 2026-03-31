from django.urls import path
from . import views

urlpatterns = [
    path('report/', views.report_incident, name='report_incident'),
    path('track/<int:incident_id>/', views.track_report, name='track_report'),
    path('my-reports/', views.my_reports, name='my_reports'),
    path('map/', views.map_view, name='map_view'),
    path('api/nearby-incidents/', views.get_nearby_incidents, name='nearby_incidents'),
]