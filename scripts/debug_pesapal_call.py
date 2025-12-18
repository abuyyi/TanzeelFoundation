import os
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanzeel.settings')

import django
django.setup()

from types import SimpleNamespace
from core import views
import json

def run():
    print('Environment PESAPAL_CONSUMER_KEY:', os.environ.get('PESAPAL_CONSUMER_KEY'))
    token, err = views.get_pesapal_access_token()
    print('get_pesapal_access_token ->', token, err)

    # create a dummy donation object
    donation = SimpleNamespace(
        pesapal_transaction_id='TESTREF123',
        amount='10.00',
        donation_type='Test',
        email='john@example.com',
        mobile_number='255700000000',
        first_name='John',
        last_name='Doe'
    )

    # For callback_url use localhost
    callback_url = 'http://127.0.0.1:8000/pesapal-callback/'
    if token:
        # Register IPN first (required) and then submit the order including the ipn id
        ipn_url = 'http://127.0.0.1:8000/pesapal-callback/'
        ipn_id, ipn_err = views.register_ipn(token, ipn_url, method='POST')
        print('register_ipn ->', ipn_id, ipn_err)

        # Also perform the submit order request directly to inspect response
        import requests, json
        submit_url = os.environ.get('PESAPAL_SUBMIT_URL', 'https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest')
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        payload = {
            'id': donation.pesapal_transaction_id,
            'currency': os.environ.get('PESAPAL_CURRENCY', 'TZS'),
            'amount': float(donation.amount),
            'description': donation.donation_type,
            'callback_url': callback_url,
            'billing_address': {
                'email_address': donation.email,
                'phone_number': donation.mobile_number,
                'first_name': donation.first_name,
                'last_name': donation.last_name,
            }
        }
        if ipn_id:
            payload['notification_id'] = ipn_id

        print('Submitting order to', submit_url)
        resp = requests.post(submit_url, headers=headers, data=json.dumps(payload), timeout=20)
        print('status', resp.status_code)
        try:
            print('json:', resp.json())
        except Exception:
            print('text:', resp.text)
    else:
        print('Skipping create_pesapal_payment since no token')

if __name__ == '__main__':
    run()
