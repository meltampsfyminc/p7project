# national/forms.py
from django import forms
from .models import Report, PastoralHouse, OfficeBuilding, OtherBuilding, Chapel

class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ['year', 'filename']
        widgets = {
            'year': forms.NumberInput(attrs={'class': 'form-control', 'min': 2000, 'max': 2100}),
            'filename': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'year': 'Report Year',
            'filename': 'File Name',
        }

class PastoralHouseForm(forms.ModelForm):
    class Meta:
        model = PastoralHouse
        fields = ['description', 'house_class', 'date_built', 'old_cost', 'add_this_year', 'sub_this_year']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Pastoral House at Main Street'}),
            'house_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A-PH'}),
            'date_built': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'old_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'add_this_year': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 0}),
            'sub_this_year': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 0}),
        }

class OfficeBuildingForm(forms.ModelForm):
    class Meta:
        model = OfficeBuilding
        fields = ['office_name', 'office_class', 'date_built', 'old_cost', 'add_this_year', 'sub_this_year']
        widgets = {
            'office_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Opisina (Ministerial, Pananalapi, Kalihiman)'}),
            'office_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., CON. (ADL-1)'}),
            'date_built': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'old_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'add_this_year': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 0}),
            'sub_this_year': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 0}),
        }

class OtherBuildingForm(forms.ModelForm):
    class Meta:
        model = OtherBuilding
        fields = ['building_name', 'building_class', 'date_built', 'old_cost', 'add_this_year', 'sub_this_year']
        widgets = {
            'building_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Pump House, Guard House'}),
            'building_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., APH-1'}),
            'date_built': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'old_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'add_this_year': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 0}),
            'sub_this_year': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 0}),
        }

class ChapelForm(forms.ModelForm):
    class Meta:
        model = Chapel
        fields = ['lokal', 'chapel_class', 'seating_capacity', 'date_built', 'last_year_cost', 'add_construction', 
                  'add_renovation', 'add_general_repair', 'add_others', 'deduction_amount', 'deduction_reason']
        widgets = {
            'lokal': forms.TextInput(attrs={'class': 'form-control'}),
            'chapel_class': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A-1, A-2, A-3'}),
            'seating_capacity': forms.NumberInput(attrs={'class': 'form-control'}),
            'date_built': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'last_year_cost': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'add_construction': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 0}),
            'add_renovation': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 0}),
            'add_general_repair': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 0}),
            'add_others': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 0}),
            'deduction_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'value': 0}),
            'deduction_reason': forms.TextInput(attrs={'class': 'form-control'}),
        }