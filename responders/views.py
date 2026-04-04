from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from reports.models import IncidentReport, IncidentUpdate
from .models import ResponderAction
from django.utils import timezone

def is_responder(user):
    return user.is_authenticated and (user.role == 'responder' or user.is_staff)

@login_required
@user_passes_test(is_responder)
def responder_dashboard(request):
    # Get incidents assigned or available
    assigned_incidents = IncidentReport.objects.filter(
        assigned_to=request.user,
        status__in=['dispatched', 'in_progress']
    )
    
    available_incidents = IncidentReport.objects.filter(
        assigned_to__isnull=True,
        status='pending'
    ).order_by('-priority', '-created_at')
    
    # Statistics
    stats = {
        'total_assigned': assigned_incidents.count(),
        'pending_responses': available_incidents.filter(priority__in=['high', 'critical']).count(),
        'resolved_today': IncidentReport.objects.filter(
            assigned_to=request.user,
            resolved_at__date=timezone.now().date()
        ).count(),
    }
    
    return render(request, 'responders/responder.html', {
        'assigned_incidents': assigned_incidents,
        'available_incidents': available_incidents,
        'stats': stats,
    })

@login_required
@user_passes_test(is_responder)
def view_incident(request, incident_id):
    incident = get_object_or_404(IncidentReport, id=incident_id)
    updates = incident.updates.all()
    actions = incident.responder_actions.all()
    
    return render(request, 'responders/view_incident.html', {
        'incident': incident,
        'updates': updates,
        'actions': actions,
    })

@login_required
@user_passes_test(is_responder)
def update_incident_status(request, incident_id):
    if request.method == 'POST':
        incident = get_object_or_404(IncidentReport, id=incident_id)
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        # Update incident
        incident.status = new_status
        if new_status == 'resolved':
            incident.resolved_at = timezone.now()
        
        if not incident.assigned_to and new_status != 'pending':
            incident.assigned_to = request.user
        
        incident.save()
        
        # Create update record
        IncidentUpdate.objects.create(
            incident=incident,
            updated_by=request.user,
            status=new_status,
            notes=notes
        )
        
        # Create responder action
        ResponderAction.objects.create(
            incident=incident,
            responder=request.user,
            action_type=get_action_type_from_status(new_status),
            notes=notes
        )
        
        messages.success(request, f'Incident status updated to {new_status}')
        
        return redirect('responder:view_incident', incident_id=incident.id)
    
    return redirect('responder:dashboard')

def get_action_type_from_status(status):
    mapping = {
        'dispatched': 'dispatched',
        'in_progress': 'arrived',
        'resolved': 'resolved',
    }
    return mapping.get(status, 'assessing')

@login_required
@user_passes_test(is_responder)
def claim_incident(request, incident_id):
    incident = get_object_or_404(IncidentReport, id=incident_id, status='pending')
    
    if not incident.assigned_to:
        incident.assigned_to = request.user
        incident.status = 'dispatched'
        incident.save()
        
        IncidentUpdate.objects.create(
            incident=incident,
            updated_by=request.user,
            status='dispatched',
            notes=f"Incident claimed by {request.user.username}"
        )
        
        messages.success(request, f'You have claimed incident: {incident.title}')
    else:
        messages.warning(request, 'This incident has already been claimed')
    
    return redirect('responder:dashboard')