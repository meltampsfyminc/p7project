from django import forms
from .models import Land

class LandForm(forms.ModelForm):
    class Meta:
        model = Land
        fields = '__all__'
