import os
import sys
import pathlib
import django

# Ensure project root is on PYTHONPATH so Django settings package can be imported
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tanzeel.settings')
django.setup()

from django.test import Client

def run():
    c = Client()
    print('GET /donate/ ->', c.get('/donate/', HTTP_HOST='127.0.0.1').status_code)
    data = {
        'amount': '10.00',
        'donation_type': 'Test donation',
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'mobile_number': '255700000000',
        'giving_frequency': 'monthly',
        'payment_method': 'mobile',
    }
    resp = c.post('/donate/', data, HTTP_HOST='127.0.0.1')
    print('POST /donate/ ->', resp.status_code)
    content = resp.content.decode(errors='replace')
    # Print a helpful excerpt
    print('\n----- Response excerpt -----\n')
    print(content[:4000])
    # quick checks for known error messages
    print('\n----- Quick checks -----')
    for probe in ['Pesapal Auth Error', 'Could not initiate payment', 'Pesapal']:
        print(probe + ':', probe in content)
    # try to extract any alert div
    import re
    m = re.search(r"<div class=\"alert alert-danger\".*?>\s*(.*?)\s*</div>", content, re.S)
    if m:
        print('\nAlert message:')
        print(m.group(1).strip())

if __name__ == '__main__':
    run()
