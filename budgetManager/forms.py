# budgetManager/forms.py
from django import forms
from .models import Items, monthlyData

class ItemsForm(forms.ModelForm):
    class Meta:
        model = Items
        fields = ['desc', 'isExpensive']
        widgets = {
            'desc': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter item description'
            }),
            'isExpensive': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'desc': 'Description',
            'isExpensive': 'Is Expensive?'
        }

class MonthlyDataForm(forms.ModelForm):
    class Meta:
        model = monthlyData
        fields = ['finYear', 'month', 'item', 'datedOn', 'amount']
        widgets = {
            'finYear': forms.Select(attrs={'class': 'form-select'}),
            'month': forms.Select(attrs={'class': 'form-select'}),
            'item': forms.Select(attrs={'class': 'form-select'}),
            'datedOn': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter amount'}),
        }
        labels = {
            'finYear': 'Financial Year',
            'month': 'Month',
            'item': 'Item',
            'datedOn': 'Date',
            'amount': 'Amount'
        }
