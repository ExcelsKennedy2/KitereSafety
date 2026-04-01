from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q
from .models import IncidentReport, IncidentUpdate
from .forms import IncidentReportForm
import json

@login_required
def report_incident(request):
    if request.method == 'POST':
        form = IncidentReportForm(request.POST, request.FILES)
        if form.is_valid():
            incident = form.save(commit=False)
            incident.reporter = request.user
            
            # Auto-assign priority based on category and description
            incident.priority = determine_priority(incident.category, incident.description)
            
            incident.save()
            
            # Handle image uploads (simplified - you'll need to implement actual file handling)
            if request.FILES.getlist('images'):
                image_urls = []
                for img in request.FILES.getlist('images'):
                    # Save image and store URL
                    pass
                incident.images = image_urls
                incident.save()
            
            messages.success(request, 'Incident reported successfully! Responders have been notified.')
            return redirect('reports:track_report', incident_id=incident.id)
        else:
            messages.error(request, 'Please fix the errors in the form before submitting.')
    else:
        form = IncidentReportForm()
    
    return render(request, 'reports/report_form.html', {'form': form})

def determine_priority(category, description):
    """Determine priority based on category and description keywords"""
    critical_keywords = ['fire', 'accident', 'attack', 'shooting', 'stab', 'bleeding', 'unconscious']
    high_keywords = ['theft', 'robbery', 'assault', 'injury', 'medical']
    
    description_lower = description.lower()
    
    if any(keyword in description_lower for keyword in critical_keywords):
        return 'critical'
    elif any(keyword in description_lower for keyword in high_keywords):
        return 'high'
    elif category and category.name.lower() in ['emergency', 'accident', 'medical']:
        return 'high'
    else:
        return 'medium'

@login_required
def track_report(request, incident_id):
    incident = get_object_or_404(IncidentReport, id=incident_id, reporter=request.user)
    updates = incident.updates.all()
    
    return render(request, 'reports/track_report.html', {
        'incident': incident,
        'updates': updates,
    })

@login_required
def my_reports(request):
    reports = IncidentReport.objects.filter(reporter=request.user)
    
    # Pagination
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'reports/my_reports.html', {'reports': page_obj})

@login_required
def get_nearby_incidents(request):
    """API endpoint for getting nearby incidents"""
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    
    if lat and lng:
        # In a real implementation, you'd use PostGIS for proper distance calculation
        incidents = IncidentReport.objects.filter(
            status__in=['pending', 'dispatched', 'in_progress']
        ).exclude(latitude=None).exclude(longitude=None)[:50]
        
        incidents_data = []
        for incident in incidents:
            incidents_data.append({
                'id': incident.id,
                'title': incident.title,
                'description': incident.description[:100],
                'latitude': float(incident.latitude) if incident.latitude else None,
                'longitude': float(incident.longitude) if incident.longitude else None,
                'status': incident.status,
                'priority': incident.priority,
                'category': incident.category.name if incident.category else 'Unknown',
                'created_at': incident.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })
        
        return JsonResponse({'incidents': incidents_data})
    
    return JsonResponse({'incidents': []})

@login_required
def map_view(request):
    return render(request, 'reports/map.html')