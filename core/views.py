import json
import logging
import re

import os
# Helper: Get Pesapal OAuth2 access token
def get_pesapal_access_token():
    # DEBUG: Print Pesapal env values
    print('PESAPAL_CONSUMER_KEY:', os.environ.get('PESAPAL_CONSUMER_KEY'))
    print('PESAPAL_CONSUMER_SECRET:', os.environ.get('PESAPAL_CONSUMER_SECRET'))
    print('PESAPAL_TOKEN_URL:', os.environ.get('PESAPAL_TOKEN_URL'))
    print('PESAPAL_SUBMIT_URL:', os.environ.get('PESAPAL_SUBMIT_URL'))
    print('PESAPAL_REGISTER_IPN_URL:', os.environ.get('PESAPAL_REGISTER_IPN_URL'))
    """Request Pesapal OAuth2 token.

    This function is tolerant of variations in response keys (e.g. 'token' or
    'access_token') and returns (token, None) on success or (None, error)
    on failure for debugging.
    """
    logger = logging.getLogger(__name__)
    pesapal_consumer_key = os.environ.get('PESAPAL_CONSUMER_KEY', '')
    pesapal_consumer_secret = os.environ.get('PESAPAL_CONSUMER_SECRET', '')
    url = os.environ.get('PESAPAL_TOKEN_URL', 'https://pay.pesapal.com/v3/api/Auth/RequestToken')
    headers = {'Content-Type': 'application/json'}
    data = {
        "consumer_key": pesapal_consumer_key,
        "consumer_secret": pesapal_consumer_secret
    }

    # Log the outgoing request details
    logger.info(f"Pesapal token request URL: {url}")
    logger.info(f"Pesapal token request headers: {headers}")
    logger.info(f"Pesapal token request data: {data}")
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=15)
    except Exception as exc:
        logger.exception('Pesapal token request failed')
        print('Pesapal token request failed:', exc)
        return None, str(exc)

    print('Pesapal token response status:', response.status_code)
    print('Pesapal token response body:', response.text)

    # Accept any 2xx as success
    if 200 <= response.status_code < 300:
        try:
            body = response.json()
        except Exception:
            return None, f'Invalid JSON from token endpoint: {response.text}'
        # common keys are 'token' or 'access_token'
        token = body.get('token') or body.get('access_token') or body.get('accessToken')
        if token:
            return token, None
        return None, f"Token not found in response: {body}"

    # Return error message for debugging
    try:
        error_detail = response.json()
    except Exception:
        error_detail = response.text
    logger.error('Pesapal token endpoint returned %s: %s', response.status_code, error_detail)
    return None, error_detail

# Helper: Create Pesapal payment request and get checkout URL
def create_pesapal_payment(donation, callback_url, access_token, notification_id=None):
    """Create an order at Pesapal and return a checkout URL.

    The implementation is defensive: accepts any 2xx response, logs full
    response for debugging, and tries multiple ways to extract a redirect URL
    (common keys, or search for the first http(s) URL in the response).
    """
    logger = logging.getLogger(__name__)
    url = os.environ.get('PESAPAL_SUBMIT_URL', 'https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest')
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    order = {
        "id": donation.pesapal_transaction_id,
        "currency": os.environ.get('PESAPAL_CURRENCY', 'TZS'),
        "amount": float(donation.amount),
        "description": donation.donation_type,
        "callback_url": callback_url,
        "billing_address": {
            "email_address": donation.email,
            "phone_number": donation.mobile_number,
            "first_name": donation.first_name,
            "last_name": donation.last_name
        }
    }
    # include notification_id only if provided (Pesapal requires a valid GUID)
    if notification_id:
        order['notification_id'] = notification_id
    # Pesapal expects the order fields at the top level (not wrapped in an "order" key)
    data = order
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=20)
    except Exception as exc:
        logger.exception('Pesapal SubmitOrderRequest failed')
        return None

    # Log for debugging
    logger.debug('Pesapal submit order status: %s, body: %s', response.status_code, response.text)

    if not (200 <= response.status_code < 300):
        return None

    # Try to parse JSON and look for known keys
    try:
        resp_json = response.json()
    except Exception:
        resp_json = None

    # Common keys returned by payment gateways
    candidates = []
    if isinstance(resp_json, dict):
        # typical key names
        candidates.extend([
            resp_json.get('redirect_url'),
            resp_json.get('checkout_url'),
            resp_json.get('payment_url'),
            resp_json.get('url'),
            resp_json.get('data', {}).get('checkout_url') if resp_json.get('data') else None,
        ])
        # also search all string values for a URL
        for v in resp_json.values():
            if isinstance(v, str) and v.startswith('http'):
                candidates.append(v)
    # Fallback: search response.text for first http(s) URL
    if not any(candidates):
        match = re.search(r'https?://[^\s"\']+', response.text or '')
        if match:
            candidates.append(match.group(0))

    # return first non-empty candidate
    for c in candidates:
        if c:
            return c
    return None


def register_ipn(access_token, ipn_url, method='POST'):
    """Register an IPN URL with Pesapal and return the ipn_id (GUID).

    Returns (ipn_id, None) on success or (None, error) on failure.
    """
    logger = logging.getLogger(__name__)
    register_url = os.environ.get('PESAPAL_REGISTER_IPN_URL', 'https://pay.pesapal.com/v3/api/URLSetup/RegisterIPN')
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    payload = {
        'url': ipn_url,
        'ipn_notification_type': method
    }
    try:
        resp = requests.post(register_url, headers=headers, data=json.dumps(payload), timeout=15)
    except Exception as exc:
        logger.exception('IPN registration failed')
        return None, str(exc)

    if not (200 <= resp.status_code < 300):
        try:
            return None, resp.json()
        except Exception:
            return None, resp.text

    try:
        body = resp.json()
    except Exception:
        return None, f'Invalid JSON from IPN register: {resp.text}'

    # Pesapal returns ipn_id or ipnId; check common keys
    ipn_id = body.get('ipn_id') or body.get('ipnId') or body.get('ipnId'.lower())
    # sometimes the response wraps fields differently; try to find GUID-like value
    if not ipn_id:
        # search for GUID in response text
        m = re.search(r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}', json.dumps(body))
        if m:
            ipn_id = m.group(0)

    if ipn_id:
        return ipn_id, None
    return None, body

import os
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from .models import SiteSettings, Donation
from .forms import DonationForm
import uuid
import requests

# Donation landing page and payment integration
def donation_view(request):
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.status = 'PENDING'
            donation.save()

            # Pesapal integration (live, with OAuth2)
            callback_url = request.build_absolute_uri(reverse('core:pesapal_callback'))

            # Generate unique reference for this donation
            reference = str(uuid.uuid4())
            donation.pesapal_transaction_id = reference
            donation.save()

            # Get OAuth2 access token
            access_token, pesapal_error = get_pesapal_access_token()
            if not access_token:
                return render(request, 'core/donation.html', {'form': form, 'error': f'Pesapal Auth Error: {pesapal_error}'})

            # Register IPN (server-to-server notification) and get notification_id
            ipn_url = request.build_absolute_uri(reverse('core:pesapal_callback'))
            notification_id, ipn_err = register_ipn(access_token, ipn_url, method='POST')
            if not notification_id:
                # Log ipn_err in server logs and surface a friendly message
                logging.getLogger(__name__).warning('Pesapal IPN registration failed: %s', ipn_err)

            # Create payment request and get checkout URL (include notification_id if present)
            pesapal_checkout_url = create_pesapal_payment(donation, callback_url, access_token, notification_id=notification_id)
            if not pesapal_checkout_url:
                return render(request, 'core/donation.html', {'form': form, 'error': 'Could not initiate payment with Pesapal. Please try again later.'})

            # If the form was submitted via AJAX, return the URL in JSON so the
            # frontend can perform the redirect client-side. Otherwise perform a
            # normal HTTP redirect.
            if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                return JsonResponse({'redirect_url': pesapal_checkout_url})

            return redirect(pesapal_checkout_url)
        else:
            # Form invalid
            return render(request, 'core/donation.html', {'form': form})
    else:
        form = DonationForm()
    return render(request, 'core/donation.html', {'form': form})

# Pesapal callback handler
@csrf_exempt
def pesapal_callback(request):
    print('Pesapal callback GET params:', dict(request.GET))
    print('Pesapal callback POST params:', dict(request.POST))
    # Use Pesapal's actual callback parameter names
    reference = request.GET.get('OrderTrackingId') or request.POST.get('OrderTrackingId')
    status = request.GET.get('status') or request.POST.get('status')
    # Only use pesapal_transaction_id for donation lookup
    donation = None
    if reference:
        donation = Donation.objects.filter(pesapal_transaction_id=reference).first()
    if donation:
        if status == 'COMPLETED' or status == 'SUCCESS':
            donation.status = 'SUCCESS'
        else:
            donation.status = 'FAILED'
        donation.save()
        return render(request, 'core/donation_status.html', {'donation': donation})
    return HttpResponse('Invalid callback', status=400)
