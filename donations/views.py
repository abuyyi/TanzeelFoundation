from django.shortcuts import render

# Create your views here.
import json
import logging
from datetime import timedelta

from django.contrib import messages
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_http_methods

from .forms import DonationForm
from .models import AzamPayWebhookEvent, Donation, PaymentTransaction
from .services.payment_service import (
    AzamPayService,
    PaymentServiceError,
    RetryablePaymentServiceError,
    WebhookVerificationError,
)


logger = logging.getLogger(__name__)


def donation_page(
    request,
    fixed_donation_type=None,
    page_heading=None,
    page_subheading=None,
    page_breadcrumb=None,
    banner_heading='Donation Policy',
    banner_description='100% of your Donation helps provide the poor with food, clean water, healthcare, education, and livelihoods.',
    template_name='donation.html',
    **kwargs,
):
    service = AzamPayService()
    transaction_ref = request.GET.get('transaction')
    latest_transaction = None
    if transaction_ref:
        latest_transaction = PaymentTransaction.objects.filter(external_id=transaction_ref).select_related('donation').first()

    form_kwargs = {}
    if fixed_donation_type:
        form_kwargs['fixed_donation_type'] = fixed_donation_type

    if request.method == 'POST':
        is_allowed, retry_after = _check_rate_limit(
            key=f"azampay:payment:{_client_identifier(request)}",
            limit=service.config['PAYMENT_RATE_LIMIT_COUNT'],
            window=service.config['PAYMENT_RATE_LIMIT_WINDOW'],
        )
        if not is_allowed:
            messages.error(request, "Too many payment attempts. Please wait a few minutes and try again.")
            response = render(
                request,
                template_name,
                {
                    'form': DonationForm(request.POST, **form_kwargs),
                    'latest_transaction': latest_transaction,
                    'page_heading': page_heading,
                    'page_subheading': page_subheading,
                    'page_breadcrumb': page_breadcrumb,
                    'banner_heading': banner_heading,
                    'banner_description': banner_description,
                    'show_to_provide_field': True,
                },
                status=429,
            )
            response['Retry-After'] = str(retry_after)
            return response

        form = DonationForm(request.POST, **form_kwargs)
        if form.is_valid():
            payment_transaction = None
            try:
                callback_url = _build_callback_url(request)
                with transaction.atomic():
                    existing_transaction = _find_duplicate_open_transaction(form.cleaned_data, service)
                    if existing_transaction:
                        messages.info(request, "A payment request is already in progress. We reopened its status page.")
                        return redirect(reverse('donations:payment_status', args=[existing_transaction.external_id]))

                    donation = form.save(commit=False)
                    if fixed_donation_type:
                        donation.donation_type = fixed_donation_type
                    donation.save()
                    external_id = PaymentTransaction.new_external_id()
                    idempotency_key = PaymentTransaction.new_external_id()
                    payment_provider = form.cleaned_data['payment_provider']
                    request_payload = {
                        'accountNumber': form.cleaned_data['mobile_number'],
                        'amount': str(form.cleaned_data['amount']),
                        'currency': service.config['CURRENCY'],
                        'externalId': external_id,
                        'provider': payment_provider,
                        'additionalProperties': {
                            'donationId': donation.pk,
                            'donorEmail': donation.email,
                            'callbackUrl': callback_url,
                        },
                    }
                    payment_transaction = PaymentTransaction.objects.create(
                        donation=donation,
                        external_id=external_id,
                        idempotency_key=idempotency_key,
                        provider=payment_provider,
                        phone_number=form.cleaned_data['mobile_number'],
                        amount=form.cleaned_data['amount'],
                        currency=service.config['CURRENCY'],
                        status=PaymentTransaction.STATUS_INITIATED,
                        initiation_attempts=1,
                        last_initiation_at=timezone.now(),
                        request_payload=request_payload,
                    )

                payment_transaction = _initiate_payment_and_persist(
                    service,
                    payment_transaction,
                    callback_url=callback_url,
                )

                if payment_transaction.status == PaymentTransaction.STATUS_SUCCESS:
                    messages.success(request, "Payment was confirmed successfully.")
                elif payment_transaction.status in {PaymentTransaction.STATUS_PENDING, PaymentTransaction.STATUS_INITIATED}:
                    messages.info(request, "Your payment request was sent successfully. Please complete the prompt on your phone.")
                elif payment_transaction.status == PaymentTransaction.STATUS_RETRYING:
                    messages.info(request, "We are retrying your payment request safely. Keep this status page open.")
                else:
                    messages.error(request, payment_transaction.gateway_message or "Payment could not be started.")

                return redirect(reverse('donations:payment_status', args=[payment_transaction.external_id]))
            except RetryablePaymentServiceError as exc:
                logger.exception(
                    "AzamPay initiation entered retrying state",
                    extra={'external_id': getattr(payment_transaction, 'external_id', None)},
                )
                if payment_transaction is not None:
                    _mark_transaction_retrying(payment_transaction, str(exc), service)
                    return redirect(reverse('donations:payment_status', args=[payment_transaction.external_id]))
                messages.error(request, "Payment could not be started right now. Please try again.")
                return render(
                    request,
                    template_name,
                    {
                        'form': form,
                        'latest_transaction': latest_transaction,
                        'page_heading': page_heading,
                        'page_subheading': page_subheading,
                        'page_breadcrumb': page_breadcrumb,
                        'banner_heading': banner_heading,
                        'banner_description': banner_description,
                        'show_to_provide_field': True,
                    },
                    status=502,
                )
            except PaymentServiceError as exc:
                logger.exception(
                    "AzamPay initiation failed",
                    extra={'external_id': getattr(payment_transaction, 'external_id', None)},
                )
                if payment_transaction is not None:
                    PaymentTransaction.objects.filter(pk=payment_transaction.pk).update(
                        status=PaymentTransaction.STATUS_ERROR,
                        gateway_message=str(exc),
                    )
                    payment_transaction.refresh_from_db(fields=['status'])
                    _update_donation_status(payment_transaction)
                messages.error(request, str(exc))
                return render(
                    request,
                    template_name,
                    {
                        'form': form,
                        'latest_transaction': latest_transaction,
                        'page_heading': page_heading,
                        'page_subheading': page_subheading,
                        'page_breadcrumb': page_breadcrumb,
                        'banner_heading': banner_heading,
                        'banner_description': banner_description,
                        'show_to_provide_field': True,
                    },
                    status=502,
                )
        else:
            logger.warning("Donation form validation failed: %s", form.errors.as_json())
            messages.error(request, "Please correct the highlighted errors and try again.")
            return render(
                request,
                template_name,
                {
                    'form': form,
                    'latest_transaction': latest_transaction,
                    'page_heading': page_heading,
                    'page_subheading': page_subheading,
                    'page_breadcrumb': page_breadcrumb,
                    'banner_heading': banner_heading,
                    'banner_description': banner_description,
                    'show_to_provide_field': True,
                },
                status=400,
            )
    else:
        form = DonationForm(**form_kwargs)

    return render(
        request,
        template_name,
        {
            'form': form,
            'latest_transaction': latest_transaction,
            'page_heading': page_heading,
            'page_subheading': page_subheading,
            'page_breadcrumb': page_breadcrumb,
            'banner_heading': banner_heading,
            'banner_description': banner_description,
            'show_to_provide_field': True,
        },
    )


@csrf_exempt
@require_http_methods(["POST"])
def azampay_webhook(request):
    service = AzamPayService()
    is_allowed, retry_after = _check_rate_limit(
        key=f"azampay:webhook:{_client_identifier(request)}",
        limit=service.config['WEBHOOK_RATE_LIMIT_COUNT'],
        window=service.config['WEBHOOK_RATE_LIMIT_WINDOW'],
    )
    if not is_allowed:
        response = JsonResponse({'detail': 'Too many webhook requests.'}, status=429)
        response['Retry-After'] = str(retry_after)
        return response

    raw_body = request.body or b'{}'
    callback_hash = service.callback_digest(raw_body)
    payload = {}
    event = AzamPayWebhookEvent.objects.create(
        event_hash=callback_hash,
        headers=_sanitize_headers(request.headers),
        processing_note='received',
    )

    try:
        payload = json.loads(raw_body.decode('utf-8') or '{}')
        event.payload = payload
        event.save(update_fields=['payload'])
        service.verify_webhook(raw_body, request.headers)
    except WebhookVerificationError as exc:
        event.processing_note = str(exc)
        event.save(update_fields=['processing_note'])
        logger.warning("Rejected AzamPay webhook", extra={'reason': str(exc), 'event_hash': callback_hash})
        return JsonResponse({'detail': 'Rejected webhook.'}, status=403)
    except json.JSONDecodeError:
        event.processing_note = 'invalid-json'
        event.save(update_fields=['processing_note'])
        logger.warning("Rejected AzamPay webhook due to invalid JSON", extra={'event_hash': callback_hash})
        return JsonResponse({'detail': 'Invalid JSON payload.'}, status=400)

    event.verification_passed = True
    external_id = _extract_external_id(payload)
    gateway_reference = service.parse_webhook_payload(payload).gateway_reference
    event.external_id = external_id
    event.gateway_reference = gateway_reference
    event.save(update_fields=['verification_passed', 'external_id', 'gateway_reference'])
    if not external_id and not gateway_reference:
        event.processing_note = 'missing-identifiers'
        event.save(update_fields=['processing_note'])
        logger.warning("AzamPay webhook missing identifiers", extra={'event_hash': callback_hash})
        return JsonResponse({'detail': 'Webhook received.'}, status=200)

    with transaction.atomic():
        transaction_qs = PaymentTransaction.objects.select_for_update()
        if external_id:
            payment_transaction = transaction_qs.filter(external_id=external_id).first()
        else:
            payment_transaction = None
        if not payment_transaction and gateway_reference:
            payment_transaction = transaction_qs.filter(gateway_reference=gateway_reference).first()
        if not payment_transaction:
            event.processing_note = 'unknown-transaction'
            event.processed = True
            event.save(update_fields=['processing_note', 'processed'])
            logger.warning(
                "AzamPay webhook for unknown transaction",
                extra={'external_id': external_id, 'gateway_reference': gateway_reference, 'event_hash': callback_hash},
            )
            return JsonResponse({'detail': 'Webhook received.'}, status=200)

        if payment_transaction.callback_hash == callback_hash:
            event.transaction = payment_transaction
            event.duplicate = True
            event.processed = True
            event.processing_note = 'duplicate'
            event.save(update_fields=['transaction', 'duplicate', 'processed', 'processing_note'])
            logger.info(
                "Duplicate AzamPay webhook ignored",
                extra={'external_id': payment_transaction.external_id, 'event_hash': callback_hash},
            )
            return JsonResponse({'detail': 'Webhook received.'}, status=200)

        parsed = service.parse_webhook_payload(payload)
        new_status = _map_status(parsed.status)
        update_fields = {
            'callback_hash': callback_hash,
            'callback_payload': payload,
            'callback_verified_at': timezone.now(),
            'gateway_status': parsed.status,
            'gateway_message': parsed.message,
        }
        if parsed.gateway_reference:
            update_fields['gateway_reference'] = parsed.gateway_reference
        if _should_advance_status(payment_transaction.status, new_status):
            update_fields['status'] = new_status
        if new_status == PaymentTransaction.STATUS_SUCCESS:
            update_fields['completed_at'] = timezone.now()

        PaymentTransaction.objects.filter(pk=payment_transaction.pk).update(**update_fields)
        payment_transaction.status = update_fields.get('status', payment_transaction.status)
        if payment_transaction.status in {
            PaymentTransaction.STATUS_SUCCESS,
            PaymentTransaction.STATUS_FAILED,
            PaymentTransaction.STATUS_CANCELLED,
            PaymentTransaction.STATUS_EXPIRED,
            PaymentTransaction.STATUS_ERROR,
        }:
            _update_donation_status(payment_transaction)
        event.transaction = payment_transaction
        event.processed = True
        event.processing_note = f'processed:{new_status}'
        event.save(update_fields=['transaction', 'processed', 'processing_note'])

    logger.info(
        "AzamPay webhook processed",
        extra={'external_id': payment_transaction.external_id, 'status': new_status, 'event_hash': callback_hash},
    )
    return JsonResponse({'detail': 'Webhook received.'}, status=200)


@require_GET
def payment_status(request, external_id):
    payment_transaction = get_object_or_404(PaymentTransaction.objects.select_related('donation'), external_id=external_id)
    return render(
        request,
        'donation_success.html',
        {
            'transaction': payment_transaction,
            'donation': payment_transaction.donation,
            'status_api_url': reverse('donations:payment_status_api', args=[payment_transaction.external_id]),
            'recover_api_url': reverse('donations:payment_recover', args=[payment_transaction.external_id]),
        },
    )


@require_GET
def payment_status_api(request, external_id):
    payment_transaction = get_object_or_404(
        PaymentTransaction.objects.only(
            'external_id',
            'status',
            'amount',
            'currency',
            'gateway_message',
            'gateway_reference',
            'updated_at',
            'next_retry_at',
            'initiation_attempts',
            'last_error_at',
        ),
        external_id=external_id,
    )
    is_recoverable = _is_recoverable(payment_transaction, AzamPayService())
    return JsonResponse(
        {
            'reference': payment_transaction.external_id,
            'status': payment_transaction.status,
            'amount': str(payment_transaction.amount),
            'currency': payment_transaction.currency,
            'message': payment_transaction.gateway_message,
            'gateway_reference': payment_transaction.gateway_reference,
            'updated_at': payment_transaction.updated_at.isoformat(),
            'is_final': payment_transaction.status in {
                PaymentTransaction.STATUS_SUCCESS,
                PaymentTransaction.STATUS_FAILED,
                PaymentTransaction.STATUS_CANCELLED,
                PaymentTransaction.STATUS_EXPIRED,
                PaymentTransaction.STATUS_ERROR,
            },
            'is_recoverable': is_recoverable,
            'next_retry_at': payment_transaction.next_retry_at.isoformat() if payment_transaction.next_retry_at else None,
            'attempts': payment_transaction.initiation_attempts,
        },
        status=200,
    )


@require_http_methods(["POST"])
def payment_recover(request, external_id):
    service = AzamPayService()
    payment_transaction = get_object_or_404(
        PaymentTransaction.objects.select_related('donation'),
        external_id=external_id,
    )
    if not _is_recoverable(payment_transaction, service):
        return JsonResponse({'detail': 'Recovery not available for this transaction.'}, status=409)

    try:
        callback_url = _build_callback_url(request)
        payment_transaction = _initiate_payment_and_persist(service, payment_transaction, callback_url=callback_url, is_retry=True)
    except RetryablePaymentServiceError as exc:
        _mark_transaction_retrying(payment_transaction, str(exc), service)
        payment_transaction.refresh_from_db(fields=['status', 'gateway_message', 'next_retry_at', 'initiation_attempts', 'updated_at'])
    except PaymentServiceError as exc:
        PaymentTransaction.objects.filter(pk=payment_transaction.pk).update(
            status=PaymentTransaction.STATUS_FAILED,
            gateway_message=str(exc),
            last_error_at=timezone.now(),
            next_retry_at=None,
        )
        payment_transaction.refresh_from_db(fields=['status', 'gateway_message', 'updated_at'])
        _update_donation_status(payment_transaction)

    return JsonResponse(
        {
            'reference': payment_transaction.external_id,
            'status': payment_transaction.status,
            'message': payment_transaction.gateway_message,
            'updated_at': payment_transaction.updated_at.isoformat(),
            'is_final': payment_transaction.status in {
                PaymentTransaction.STATUS_SUCCESS,
                PaymentTransaction.STATUS_FAILED,
                PaymentTransaction.STATUS_ERROR,
            },
            'is_recoverable': _is_recoverable(payment_transaction, service),
            'next_retry_at': payment_transaction.next_retry_at.isoformat() if payment_transaction.next_retry_at else None,
        },
        status=200,
    )


def _map_status(status):
    normalized = (status or '').lower()
    if normalized in {'success', 'successful', 'completed'}:
        return PaymentTransaction.STATUS_SUCCESS
    if normalized in {'processing'}:
        return PaymentTransaction.STATUS_PROCESSING
    if normalized in {'pending', 'initiated', 'created'}:
        return PaymentTransaction.STATUS_PENDING
    if normalized in {'retrying'}:
        return PaymentTransaction.STATUS_RETRYING
    if normalized in {'failed', 'error', 'rejected'}:
        return PaymentTransaction.STATUS_FAILED
    if normalized in {'cancelled', 'canceled'}:
        return PaymentTransaction.STATUS_CANCELLED
    if normalized in {'expired'}:
        return PaymentTransaction.STATUS_EXPIRED
    return PaymentTransaction.STATUS_ERROR


def _should_advance_status(current_status, new_status):
    order = {
        PaymentTransaction.STATUS_CREATED: 0,
        PaymentTransaction.STATUS_INITIATED: 1,
        PaymentTransaction.STATUS_PENDING: 2,
        PaymentTransaction.STATUS_RETRYING: 2,
        PaymentTransaction.STATUS_PROCESSING: 3,
        PaymentTransaction.STATUS_SUCCESS: 4,
        PaymentTransaction.STATUS_FAILED: 4,
        PaymentTransaction.STATUS_CANCELLED: 4,
        PaymentTransaction.STATUS_EXPIRED: 4,
        PaymentTransaction.STATUS_ERROR: 4,
    }
    return order.get(new_status, 0) >= order.get(current_status, 0)


def _extract_external_id(payload):
    data = payload.get('data') or {}
    properties = data.get('properties') or {}
    for candidate in (
        payload.get('externalId'),
        payload.get('referenceId'),
        payload.get('externalreference'),
        payload.get('externalReference'),
        data.get('externalId'),
        data.get('referenceId'),
        data.get('externalreference'),
        data.get('externalReference'),
        properties.get('externalId'),
        properties.get('referenceId'),
        properties.get('externalreference'),
        properties.get('externalReference'),
    ):
        if candidate:
            return str(candidate)
    return ''


def _client_identifier(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


def _check_rate_limit(key, limit, window):
    now = int(timezone.now().timestamp())
    bucket = now // max(window, 1)
    cache_key = f"{key}:{bucket}"
    try:
        count = cache.incr(cache_key)
    except ValueError:
        cache.set(cache_key, 1, timeout=window)
        count = 1
    retry_after = max(window - (now % max(window, 1)), 1)
    return count <= limit, retry_after


def _sanitize_headers(headers):
    redacted = {}
    sensitive = {'authorization', 'cookie'}
    for key, value in headers.items():
        if key.lower() in sensitive:
            redacted[key] = '[redacted]'
        else:
            redacted[key] = value
    return redacted


def _build_callback_url(request):
    public_base_url = request.scheme + '://' + request.get_host()
    configured_public_base_url = settings.AZAMPAY.get('PUBLIC_BASE_URL')
    if configured_public_base_url:
        public_base_url = configured_public_base_url.rstrip('/')
    return f"{public_base_url}{reverse('donations:azampay_webhook')}"


def _initiate_payment_and_persist(service, payment_transaction, callback_url, is_retry=False):
    if is_retry:
        payment_transaction.initiation_attempts += 1
        payment_transaction.last_initiation_at = timezone.now()
        payment_transaction.save(update_fields=['initiation_attempts', 'last_initiation_at', 'updated_at'])
    gateway_response = service.initiate_checkout(
        payment_transaction,
        callback_url=callback_url,
        payload=payment_transaction.request_payload,
    )
    payment_transaction.status = _map_status(gateway_response.status)
    payment_transaction.gateway_reference = gateway_response.gateway_reference
    payment_transaction.gateway_status = gateway_response.status
    payment_transaction.gateway_message = gateway_response.message
    payment_transaction.response_payload = gateway_response.payload
    payment_transaction.next_retry_at = None
    payment_transaction.last_error_at = None
    payment_transaction.last_initiation_at = timezone.now()
    payment_transaction.save(
        update_fields=[
            'status',
            'gateway_reference',
            'gateway_status',
            'gateway_message',
            'response_payload',
            'next_retry_at',
            'last_error_at',
            'initiation_attempts',
            'last_initiation_at',
            'updated_at',
        ]
    )
    if payment_transaction.status in {
        PaymentTransaction.STATUS_SUCCESS,
        PaymentTransaction.STATUS_FAILED,
        PaymentTransaction.STATUS_CANCELLED,
        PaymentTransaction.STATUS_EXPIRED,
        PaymentTransaction.STATUS_ERROR,
    }:
        _update_donation_status(payment_transaction)
    return payment_transaction


def _update_donation_status(payment_transaction):
    donation = payment_transaction.donation
    if payment_transaction.status == PaymentTransaction.STATUS_SUCCESS:
        target_status = Donation.DONATION_STATUS_COMPLETED
    elif payment_transaction.status in {
        PaymentTransaction.STATUS_FAILED,
        PaymentTransaction.STATUS_ERROR,
    }:
        target_status = Donation.DONATION_STATUS_FAILED
    elif payment_transaction.status == PaymentTransaction.STATUS_CANCELLED:
        target_status = Donation.DONATION_STATUS_CANCELLED
    elif payment_transaction.status == PaymentTransaction.STATUS_EXPIRED:
        target_status = Donation.DONATION_STATUS_EXPIRED
    else:
        target_status = Donation.DONATION_STATUS_PENDING

    if donation.status != target_status:
        donation.status = target_status
        donation.save(update_fields=['status', 'updated_at'])


def _mark_transaction_retrying(payment_transaction, message, service):
    retry_delay = service.config['INITIAL_RETRY_DELAY_SECONDS'] * max(payment_transaction.initiation_attempts, 1)
    max_attempts = service.config['MAX_INITIATION_RETRIES']
    next_status = PaymentTransaction.STATUS_RETRYING if payment_transaction.initiation_attempts < max_attempts else PaymentTransaction.STATUS_FAILED
    next_retry_at = timezone.now() + timedelta(seconds=retry_delay) if next_status == PaymentTransaction.STATUS_RETRYING else None
    PaymentTransaction.objects.filter(pk=payment_transaction.pk).update(
        status=next_status,
        gateway_message=message,
        last_error_at=timezone.now(),
        next_retry_at=next_retry_at,
    )
    if next_status in {
        PaymentTransaction.STATUS_FAILED,
        PaymentTransaction.STATUS_CANCELLED,
        PaymentTransaction.STATUS_EXPIRED,
    }:
        payment_transaction.status = next_status
        _update_donation_status(payment_transaction)


def _find_duplicate_open_transaction(cleaned_data, service):
    window_start = timezone.now() - timedelta(seconds=service.config['DUPLICATE_ATTEMPT_WINDOW_SECONDS'])
    return PaymentTransaction.objects.filter(
        donation__email=cleaned_data['email'],
        phone_number=cleaned_data['mobile_number'],
        amount=cleaned_data['amount'],
        provider=cleaned_data['payment_provider'],
        status__in=[
            PaymentTransaction.STATUS_INITIATED,
            PaymentTransaction.STATUS_PENDING,
            PaymentTransaction.STATUS_RETRYING,
            PaymentTransaction.STATUS_PROCESSING,
        ],
        created_at__gte=window_start,
    ).order_by('-created_at').first()


def _is_recoverable(payment_transaction, service):
    if payment_transaction.status in {
        PaymentTransaction.STATUS_SUCCESS,
        PaymentTransaction.STATUS_CANCELLED,
        PaymentTransaction.STATUS_EXPIRED,
        PaymentTransaction.STATUS_ERROR,
    }:
        return False
    if payment_transaction.status == PaymentTransaction.STATUS_RETRYING:
        return bool(payment_transaction.next_retry_at and payment_transaction.next_retry_at <= timezone.now())
    if payment_transaction.status == PaymentTransaction.STATUS_PENDING:
        if payment_transaction.updated_at <= timezone.now() - timedelta(seconds=service.config['PENDING_STALE_AFTER_SECONDS']):
            return True
    return payment_transaction.initiation_attempts < service.config['MAX_INITIATION_RETRIES']


