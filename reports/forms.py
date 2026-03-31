from django import forms
from .models import IncidentReport, IncidentCategory

class IncidentReportForm(forms.ModelForm):
    class Meta:
        model = IncidentReport
        fields = ['category', 'title', 'description', 'location_name', 'latitude', 'longitude']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = IncidentCategory.objects.all()
        self.fields['category'].empty_label = "Select Category" 