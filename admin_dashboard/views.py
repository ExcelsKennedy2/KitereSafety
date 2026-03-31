from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q, Avg, F
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from datetime import timedelta
from reports.models import IncidentReport, IncidentCategory
from users.models import User
import pandas as pd
import json
from collections import defaultdict

@staff_member_required
def dashboard_index(request):
    # Get date filters
    days = request.GET.get('days', 30)
    try:
        days = int(days)
    except:
        days = 30
    
    start_date = timezone.now() - timedelta(days=days)
    
    # Basic statistics
    total_reports = IncidentReport.objects.filter(created_at__gte=start_date).count()
    resolved_reports = IncidentReport.objects.filter(
        created_at__gte=start_date,
        status='resolved'
    ).count()
    pending_reports = IncidentReport.objects.filter(
        created_at__gte=start_date,
        status__in=['pending', 'dispatched', 'in_progress']
    ).count()
    active_responders = User.objects.filter(role='responder', is_active=True).count()
    
    # Response time analysis
    resolved_incidents = IncidentReport.objects.filter(
        resolved_at__isnull=False,
        created_at__gte=start_date
    )
    
    response_times = []
    for incident in resolved_incidents:
        response_time = (incident.resolved_at - incident.created_at).total_seconds() / 3600  # hours
        response_times.append(response_time)
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Incident trends over time
    daily_trends = IncidentReport.objects.filter(created_at__gte=start_date) \
        .annotate(date=TruncDate('created_at')) \
        .values('date') \
        .annotate(count=Count('id')) \
        .order_by('date')
    
    # Incidents by category
    category_stats = IncidentReport.objects.filter(created_at__gte=start_date) \
        .values('category__name') \
        .annotate(count=Count('id')) \
        .order_by('-count')
    
    # Priority distribution
    priority_stats = IncidentReport.objects.filter(created_at__gte=start_date) \
        .values('priority') \
        .annotate(count=Count('id'))
    
    # Status distribution
    status_stats = IncidentReport.objects.filter(created_at__gte=start_date) \
        .values('status') \
        .annotate(count=Count('id'))
    
    # Hotspots - incidents by location
    hotspots = []
    incidents_with_location = IncidentReport.objects.filter(
        created_at__gte=start_date,
        latitude__isnull=False,
        longitude__isnull=False
    ).exclude(latitude=0, longitude=0)[:100]
    
    for incident in incidents_with_location:
        hotspots.append({
            'lat': float(incident.latitude),
            'lng': float(incident.longitude),
            'title': incident.title,
            'category': incident.category.name if incident.category else 'Unknown',
            'priority': incident.priority,
            'status': incident.status,
        })
    
    # Time-based analysis (hourly patterns)
    hourly_patterns = defaultdict(int)
    incidents_by_hour = IncidentReport.objects.filter(created_at__gte=start_date)
    for incident in incidents_by_hour:
        hour = incident.created_at.hour
        hourly_patterns[hour] += 1
    
    # Prepare data for charts
    chart_data = {
        'daily_trends': {
            'dates': [item['date'].strftime('%Y-%m-%d') for item in daily_trends],
            'counts': [item['count'] for item in daily_trends],
        },
        'category_data': {
            'labels': [item['category__name'] or 'Uncategorized' for item in category_stats],
            'values': [item['count'] for item in category_stats],
        },
        'priority_data': {
            'labels': [item['priority'].capitalize() for item in priority_stats],
            'values': [item['count'] for item in priority_stats],
        },
        'status_data': {
            'labels': [item['status'].capitalize() for item in status_stats],
            'values': [item['count'] for item in status_stats],
        },
        'hourly_patterns': {
            'hours': list(range(24)),
            'counts': [hourly_patterns[h] for h in range(24)],
        },
    }
    
    # Predictive analytics - simple trend prediction
    if len(daily_trends) >= 7:
        df = pd.DataFrame(list(daily_trends))
        df['date_num'] = range(len(df))
        
        # Simple linear regression for prediction
        from sklearn.linear_model import LinearRegression
        X = df[['date_num']].values
        y = df['count'].values
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next 7 days
        future_dates = range(len(df), len(df) + 7)
        predictions = model.predict([[d] for d in future_dates])
        
        prediction_data = {
            'dates': [(timezone.now() + timedelta(days=i+1)).strftime('%Y-%m-%d') for i in range(7)],
            'predictions': [max(0, int(p)) for p in predictions],
        }
    else:
        prediction_data = None
    
    context = {
        'total_reports': total_reports,
        'resolved_reports': resolved_reports,
        'pending_reports': pending_reports,
        'active_responders': active_responders,
        'avg_response_time': round(avg_response_time, 1),
        'resolution_rate': round((resolved_reports / total_reports * 100), 1) if total_reports > 0 else 0,
        'chart_data': json.dumps(chart_data),
        'hotspots': json.dumps(hotspots),
        'prediction_data': json.dumps(prediction_data) if prediction_data else None,
        'days': days,
    }
    
    return render(request, 'admin/index.html', context)

@staff_member_required
def reports_list(request):
    reports = IncidentReport.objects.all().order_by('-created_at')
    
    # Filtering
    status = request.GET.get('status')
    if status:
        reports = reports.filter(status=status)
    
    category = request.GET.get('category')
    if category:
        reports = reports.filter(category__id=category)
    
    priority = request.GET.get('priority')
    if priority:
        reports = reports.filter(priority=priority)
    
    categories = IncidentCategory.objects.all()
    
    return render(request, 'admin/reports_list.html', {
        'reports': reports,
        'categories': categories,
    })

@staff_member_required
def users_management(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'admin/users.html', {'users': users})