import re
from decimal import Decimal, InvalidOperation

from django import forms
from django.core.validators import validate_email

from .models import Donation


PHONE_RE = re.compile(r"^(?:\+?255|0)\d{9}$")

PAYMENT_PROVIDER_CHOICES = [
    ('', 'Choose provider'),
    ('Mpesa', 'M-Pesa'),
    ('Airtel', 'Airtel Money'),
    ('Tigo', 'Tigo Pesa'),
    ('Halotel', 'HaloPesa'),
]

PAYMENT_METHOD_CHOICES = [
    ('azampesa', 'AzamPesa'),
    ('mobile_money', 'Mobile Money'),
]

GIVING_FREQUENCY_CHOICES = [
    ('one-off', 'One-off'),
    ('every-day', 'Every Day'),
    ('every-friday', 'Every Friday'),
    ('every-month', 'Every Month'),
]


class DonationForm(forms.ModelForm):
    CURRENCY_CHOICES = [
        ('TSH', 'TSH'),
        ('$', '$'),
        ('€', '€'),
    ]

    giving_frequency = forms.ChoiceField(
        choices=GIVING_FREQUENCY_CHOICES,
        widget=forms.RadioSelect,
        initial='one-off',
        label='Donation Frequency',
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect,
        initial='azampesa',
    )
    payment_provider = forms.ChoiceField(
        choices=PAYMENT_PROVIDER_CHOICES,
        widget=forms.Select(attrs={'class': 'form-input'}),
        required=False,
    )

    class Meta:
        model = Donation
        fields = [
            'title', 'first_name', 'last_name', 'email', 'mobile_number', 'is_organization',
            'country', 'postcode', 'donation_type', 'amount', 'in_country', 'to_provide',
            'giving_frequency', 'age_confirmation', 'gift_aid', 'agree_to_terms'
        ]
        widgets = {
            'title': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'}),
            'is_organization': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'country': forms.Select(attrs={'class': 'form-select'}),
            'postcode': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Postcode'}),
            'donation_type': forms.Select(attrs={'class': 'form-input', 'placeholder': 'Donation Type'}),
            'amount': forms.NumberInput(attrs={'class': 'form-input donation-amount', 'min': 2000, 'placeholder': 'Amount', 'step': '0.01'}),
            'in_country': forms.Select(attrs={'class': 'form-input', 'aria-label': 'Country or Region'}),
            'to_provide': forms.Select(attrs={'class': 'form-input', 'aria-label': 'Provider'}),
            'age_confirmation': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'gift_aid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'agree_to_terms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, fixed_donation_type=None, fixed_to_provide=None, **kwargs):
        self.fixed_donation_type = fixed_donation_type or fixed_to_provide
        self.fixed_to_provide = fixed_to_provide
        super().__init__(*args, **kwargs)
        
        # Remove empty choices from all select fields
        self.fields['title'].choices = [c for c in self.fields['title'].choices if c[0] != '']
        
        if self.fixed_donation_type:
            self.fields['donation_type'].choices = [(self.fixed_donation_type, self.fixed_donation_type)]
            self.fields['donation_type'].initial = self.fixed_donation_type
        else:
            # Filter out any existing empty choices and add custom placeholder
            donation_type_choices = [c for c in self.fields['donation_type'].choices if c[0] != '']
            self.fields['donation_type'].choices = [('', 'Donation Type')] + donation_type_choices

        # Filter out any existing empty choices from country and provider fields
        in_country_choices = [c for c in self.fields['in_country'].choices if c[0] != '']
        self.fields['in_country'].choices = [('', 'Country or Region')] + in_country_choices
        
        to_provide_choices = [c for c in self.fields['to_provide'].choices if c[0] != '']
        self.fields['to_provide'].choices = [('', 'Provider')] + to_provide_choices

        for field_name in ('country', 'postcode', 'gift_aid', 'agree_to_terms'):
            self.fields[field_name].required = False

    def clean_donation_type(self):
        donation_type = self.cleaned_data.get('donation_type')
        valid_donation_types = {choice[0] for choice in Donation.DONATION_TYPE_CHOICES}
        if self.fixed_donation_type:
            if self.fixed_donation_type not in valid_donation_types:
                raise forms.ValidationError('Invalid donation type.')
            return self.fixed_donation_type
        if not donation_type:
            raise forms.ValidationError('Choose a donation type.')
        if donation_type not in valid_donation_types:
            raise forms.ValidationError('Choose a valid donation type.')
        return donation_type

    def clean_to_provide(self):
        provider = self.cleaned_data.get('to_provide')
        valid_providers = {choice[0] for choice in Donation.PROVIDE_CHOICES}
        if self.fixed_to_provide:
            if self.fixed_to_provide not in valid_providers:
                raise forms.ValidationError('Invalid donation target.')
            return self.fixed_to_provide
        if not provider:
            raise forms.ValidationError('Choose a project or provider.')
        if provider not in valid_providers:
            raise forms.ValidationError('Choose a valid project or provider.')
        return provider

    def _get_selected_currency(self):
        if hasattr(self.data, 'getlist'):
            currencies = self.data.getlist('currency')
            for currency in currencies:
                if currency:
                    return currency
        else:
            currency = self.data.get('currency')
            if currency:
                return currency
        return 'TSH'

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None:
            raise forms.ValidationError("Enter a valid amount.")
        try:
            amount = Decimal(amount)
        except (TypeError, InvalidOperation):
            raise forms.ValidationError("Enter a valid amount.")

        currency = self._get_selected_currency()
        minimum_amount = Decimal('2000') if currency == 'TSH' else Decimal('1')
        if amount < minimum_amount:
            if currency == 'TSH':
                raise forms.ValidationError("Amount must be at least Tsh.2000.")
            raise forms.ValidationError(f"Amount must be at least {currency}1.")
        return amount

    def clean_mobile_number(self):
        mobile_number = re.sub(r"\s+", "", self.cleaned_data.get('mobile_number', ''))
        if not PHONE_RE.match(mobile_number):
            raise forms.ValidationError("Enter a valid Tanzanian phone number, for example 07XXXXXXXX or 2557XXXXXXXX.")
        if mobile_number.startswith('+'):
            mobile_number = mobile_number[1:]
        if mobile_number.startswith('0'):
            mobile_number = f"255{mobile_number[1:]}"
        return mobile_number

    def clean_payment_provider(self):
        provider = self.cleaned_data.get('payment_provider')
        payment_method = self.cleaned_data.get('payment_method')
        if payment_method == 'azampesa':
            return 'AzamPesa'

        valid_providers = {choice[0] for choice in PAYMENT_PROVIDER_CHOICES}
        if not provider:
            raise forms.ValidationError("Choose a mobile money provider.")
        if provider not in valid_providers:
            raise forms.ValidationError("Choose a valid mobile money provider.")
        return provider

    def clean_first_name(self):
        return self._clean_name_field('first_name')

    def clean_last_name(self):
        return self._clean_name_field('last_name')

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        validate_email(email)
        return email

    def clean_postcode(self):
        postcode = re.sub(r"\s+", " ", (self.cleaned_data.get('postcode') or '').strip())
        return postcode

    def _clean_name_field(self, field_name):
        value = re.sub(r"\s+", " ", (self.cleaned_data.get(field_name) or '').strip())
        if not value:
            raise forms.ValidationError("This field is required.")
        if not re.fullmatch(r"[A-Za-z][A-Za-z\s'\-]{0,99}", value):
            raise forms.ValidationError("Enter a valid name.")
        return value

    def clean_age_confirmation(self):
        age_confirmation = self.cleaned_data.get('age_confirmation')
        if not age_confirmation:
            raise forms.ValidationError("You must confirm that you are 18 years of age or older.")
        return age_confirmation

    def save(self, commit=True):
        donation = super().save(commit=False)
        if self.fixed_to_provide:
            donation.to_provide = self.fixed_to_provide
        if not donation.country:
            donation.country = donation.in_country or 'Tanzania'
        if not donation.postcode:
            donation.postcode = 'N/A'
        donation.card_number = ''
        donation.expiry_date = ''
        donation.security_code = ''
        donation.contact_email = donation.contact_email or False
        donation.contact_sms = donation.contact_sms or False
        donation.contact_whatsapp = donation.contact_whatsapp or False
        donation.contact_post = donation.contact_post or False
        donation.agree_to_terms = bool(donation.agree_to_terms)
        if commit:
            donation.save()
        return donation
