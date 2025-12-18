from django import forms
from .models import Donation

class DonationForm(forms.ModelForm):
    class Meta:
        model = Donation
        fields = [
            'amount', 'donation_type', 'first_name', 'last_name', 'email',
            'mobile_number', 'giving_frequency', 'payment_method'
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01', 'placeholder': 'Amount'}),
            'donation_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Donation Type'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'giving_frequency': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }
