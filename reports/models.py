from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class IncidentCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-exclamation-triangle')
    color = models.CharField(max_length=7, default='#ff0000')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Incident Categories"

class IncidentReport(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('dispatched', 'Dispatched'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )
    
    PRIORITY_CHOICES = (
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    )
    
    # Basic Information
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reports')
    category = models.ForeignKey(IncidentCategory, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Location Information
    location_name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    
    # Media
    images = models.JSONField(default=list)  # Store multiple image URLs
    video_url = models.URLField(blank=True)
    
    # Status Tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_incidents')
    
    # Response Information
    responder_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.status}"
    
    # def save(self, *args, **kwargs):
    #     if self.latitude and self.longitude:
    #         from django.contrib.gis.geos import Point
    #         self.location_point = Point(float(self.longitude), float(self.latitude))
    #     super().save(*args, **kwargs)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']

class IncidentUpdate(models.Model):
    incident = models.ForeignKey(IncidentReport, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=IncidentReport.STATUS_CHOICES)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Update for {self.incident.title} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']