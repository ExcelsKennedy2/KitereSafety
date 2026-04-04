from django.urls import path
from . import views

app_name = 'responder'

urlpatterns = [
    path('dashboard/', views.responder_dashboard, name='dashboard'),
    path('incident/<int:incident_id>/', views.view_incident, name='view_incident'),
    path('incident/<int:incident_id>/update/', views.update_incident_status, name='update_status'),
    path('incident/<int:incident_id>/claim/', views.claim_incident, name='claim_incident'),
]