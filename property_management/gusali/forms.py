from django import forms
from .models import Building, BuildingYearlyRecord

class BuildingForm(forms.ModelForm):
    class Meta:
        model = Building
        fields = '__all__'
        widgets = {
            'donation_date': forms.DateInput(attrs={'type': 'date'}),
            'ownership_date': forms.DateInput(attrs={'type': 'date'}),
        }

class BuildingYearlyRecordForm(forms.ModelForm):
    class Meta:
        model = BuildingYearlyRecord
        fields = '__all__'
        exclude = ['building']
