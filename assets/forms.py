from django import forms
from .models import dividentDetails

class DividentDetailsForm(forms.ModelForm):
    class Meta:
        model = dividentDetails
        fields = ['finYear', 'divDate', 'stock', 'amount']

        widgets = {
            'finYear': forms.Select(attrs={
                'class': 'form-control form-control-lg'
            }),
            'divDate': forms.DateInput(attrs={
                'class': 'form-control form-control-lg',
                'type': 'date'
            }),
            'stock': forms.Select(attrs={
                'class': 'form-control form-control-lg searchable'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control form-control-lg',
                'step': '0.0000000001',
                'placeholder': 'Enter amount'
            }),
        }
