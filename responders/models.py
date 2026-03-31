from django.db import models
from django.contrib.auth import get_user_model
from reports.models import IncidentReport

User = get_user_model()

class ResponderTeam(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    team_lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='led_teams')
    members = models.ManyToManyField(User, related_name='teams')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class ResponderAction(models.Model):
    ACTION_TYPES = (
        ('dispatched', 'Dispatched'),
        ('arrived', 'Arrived'),
        ('assessing', 'Assessing'),
        ('assisting', 'Assisting'),
        ('resolved', 'Resolved'),
        ('escalated', 'Escalated'),
    )
    
    incident = models.ForeignKey(IncidentReport, on_delete=models.CASCADE, related_name='responder_actions')
    responder = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions')
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES)
    notes = models.TextField(blank=True)
    location_update = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.responder.username} - {self.action_type} - {self.incident.title}"
    
    class Meta:
        ordering = ['-created_at']