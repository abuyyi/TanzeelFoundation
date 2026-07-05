from django.test import TestCase

from .forms import DonationForm


class DonationFormCurrencyTests(TestCase):
    def test_dollar_currency_allows_smaller_amounts(self):
        form = DonationForm(
            data={
                'title': 'Mr',
                'first_name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'mobile_number': '0712345678',
                'is_organization': False,
                'country': 'Tanzania',
                'postcode': '12345',
                'donation_type': 'General Fund',
                'amount': '10',
                'in_country': 'Tanzania',
                'to_provide': 'Social Service',
                'giving_frequency': 'one-off',
                'age_confirmation': 'on',
                'gift_aid': '',
                'agree_to_terms': 'on',
                'payment_method': 'azampesa',
                'payment_provider': '',
                'currency': '$',
            }
        )

        self.assertTrue(form.is_valid(), form.errors)
