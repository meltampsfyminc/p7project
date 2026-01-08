from django import forms
from .models import Item

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = '__all__'
        widgets = {
            'date_acquired': forms.DateInput(attrs={'type': 'date'}),
        }
