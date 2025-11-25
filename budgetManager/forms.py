# budgetManager/forms.py
from django import forms
from .models import *

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


class DebtManagerForm(forms.ModelForm):
    class Meta:
        model = DebtManager
        fields = [
            'debtGivenDate',
            'debtGivenTo',
            'debtGivenAmount',
            'debtPaidDate',
            'isPaid'
        ]
        widgets = {
            'debtGivenDate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'debtGivenTo': forms.TextInput(attrs={'class': 'form-control'}),
            'debtGivenAmount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'debtPaidDate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'isPaid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class LoanManagerForm(forms.ModelForm):
    class Meta:
        model = LoanManager
        fields = [
            'loanTakenDate',
            'loanTakenFrom',
            'loanAmount',
            'loanInterest',
            'isClosed',
        ]
        widgets = {
            'loanTakenDate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'loanTakenFrom': forms.TextInput(attrs={'class': 'form-control'}),
            'loanAmount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'loanInterest': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'isClosed': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # These fields are excluded from validation if they exist
            if 'loanAmountPaid' in self.fields:
                self.fields['loanAmountPaid'].required = False
            if 'loanPaidDate' in self.fields:
                self.fields['loanPaidDate'].required = False

class LoanTransForm(forms.ModelForm):
    class Meta:
        model = LoanTrans
        fields = ['payedOn', 'loanName', 'amount']

        widgets = {
            'payedOn': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'loanName': forms.Select(attrs={'class': 'form-select'}), 
            'amount': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter dropdown
        self.fields['loanName'].queryset = LoanManager.objects.filter(isClosed=False)