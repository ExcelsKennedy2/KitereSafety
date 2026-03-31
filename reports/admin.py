from django.contrib import admin
from .models import IncidentCategory, IncidentReport, IncidentUpdate
# Register your models here.
admin.site.register(IncidentCategory)
admin.site.register(IncidentReport)
admin.site.register(IncidentUpdate)