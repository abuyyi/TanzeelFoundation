import base64
import hashlib
import json
import logging
import socket
import hmac
import importlib.util
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone as dt_timezone
from urllib import error, request

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone


logger = logging.getLogger(__name__)
HTTPX_AVAILABLE = bool(importlib.util.find_spec('httpx'))


class PaymentServiceError(Exception):
    pass


class RetryablePaymentServiceError(PaymentServiceError):
    pass


class WebhookVerificationError(PaymentServiceError):
    pass


@dataclass
class GatewayResponse:
    ok: bool
    status: str
    message: str
    payload: dict
    gateway_reference: str = ''


class AzamPayService:
    def __init__(self):
        self.config = settings.AZAMPAY
        self.timeout = self.config['TIMEOUT']
        self.auth_timeout = self.config.get('AUTH_TIMEOUT', self.timeout)
        self.checkout_timeout = self.config.get('CHECKOUT_TIMEOUT', self.timeout)

    def validate_configuration(self):
        missing = [
            key for key in ('APP_NAME', 'CLIENT_ID', 'CLIENT_SECRET')
            if not self.config.get(key)
        ]
        if missing:
            raise PaymentServiceError(
                f"Missing AzamPay configuration: {', '.join(missing)}. Set them in your environment or .env file."
            )

    def initiate_checkout(self, transaction, callback_url=None, payload=None):
        if self.config.get('MOCK_MODE'):
            logger.info(
                "AzamPay mock checkout mode enabled",
                extra={'external_id': transaction.external_id},
            )
            return self._mock_checkout(transaction, payload=payload, callback_url=callback_url)

        self.validate_configuration()
        token = self.get_access_token()
        payload = payload or self.build_checkout_payload(transaction, callback_url=callback_url)
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'Idempotency-Key': transaction.idempotency_key,
        }
        if self.config.get('API_KEY'):
            headers['X-API-Key'] = self.config['API_KEY']

        checksum = self.generate_checksum(payload)
        if checksum:
            headers[self.config['CHECKSUM_HEADER']] = checksum

        request_url = f"{self.config['CHECKOUT_BASE_URL'].rstrip('/')}/azampay/mno/checkout"
        logger.debug(
            "AzamPay checkout request",
            extra={
                'url': request_url,
                'headers': self._sanitize_payload(headers),
                'payload': self._sanitize_payload(payload),
                'external_id': transaction.external_id,
            },
        )
        response = self._post_json(
            request_url,
            payload,
            headers=headers,
            timeout=self.checkout_timeout,
        )
        gateway_response = self.parse_checkout_response(response)
        logger.info(
            "AzamPay checkout response",
            extra={
                'external_id': transaction.external_id,
                'status': gateway_response.status,
                'gateway_reference': gateway_response.gateway_reference,
                'response': self._sanitize_payload(response),
            },
        )
        return gateway_response

    def get_access_token(self):
        cached_token = cache.get(self.config['TOKEN_CACHE_KEY'])
        if cached_token:
            return cached_token

        payload = {
            'appName': self.config['APP_NAME'],
            'clientId': self.config['CLIENT_ID'],
            'clientSecret': self.config['CLIENT_SECRET'],
        }
        response = self._post_json(
            f"{self.config['AUTH_BASE_URL'].rstrip('/')}/AppRegistration/GenerateToken",
            payload,
            headers={'Content-Type': 'application/json'},
            timeout=self.auth_timeout,
        )
        token = (((response.get('data') or {}).get('accessToken')) or response.get('accessToken') or '').strip()
        if not token:
            logger.error("AzamPay token response missing access token", extra={'response': self._sanitize_payload(response)})
            raise PaymentServiceError("Could not authenticate with AzamPay.")
        expires_in = self._extract_token_ttl(response)
        cache.set(self.config['TOKEN_CACHE_KEY'], token, timeout=max(expires_in - 30, 30))
        return token

    def build_checkout_payload(self, transaction, callback_url=None):
        payload = {
            'accountNumber': transaction.phone_number,
            'amount': str(transaction.amount),
            'currency': transaction.currency,
            'externalId': transaction.external_id,
            'provider': transaction.provider,
            'additionalProperties': {
                'donationId': transaction.donation_id,
                'donorEmail': transaction.donation.email,
            },
        }
        if callback_url:
            payload['callbackUrl'] = callback_url
            payload['callbackURL'] = callback_url
            payload['additionalProperties']['callbackUrl'] = callback_url
        return payload

    def _mock_checkout(self, transaction, payload=None, callback_url=None):
        payload = payload or self.build_checkout_payload(transaction, callback_url=callback_url)
        gateway_reference = payload.get('externalId') or f"mock-{transaction.external_id}"
        mock_payload = {
            'success': True,
            'message': 'Mock checkout created.',
            'status': 'pending',
            'externalId': transaction.external_id,
            'reference': gateway_reference,
            'data': {
                'externalId': transaction.external_id,
                'reference': gateway_reference,
                'status': 'pending',
            },
        }
        return GatewayResponse(
            ok=True,
            status='pending',
            message='Mock AzamPay checkout created.',
            payload=mock_payload,
            gateway_reference=gateway_reference,
        )

    def parse_checkout_response(self, payload):
        success_flag = bool(payload.get('success'))
        status = self._extract_status(payload)
        if status == 'success':
            status = 'processing'
        if status is None:
            status = 'processing' if success_flag else 'failed'

        message = payload.get('message') or payload.get('detail') or 'Payment request sent to AzamPay.'
        gateway_reference = self._extract_reference(payload)

        return GatewayResponse(
            ok=status not in {'failed', 'error', 'cancelled', 'expired'},
            status=status,
            message=message,
            payload=payload,
            gateway_reference=gateway_reference,
        )

    def parse_webhook_payload(self, payload):
        status = self._extract_status(payload)
        if status is None:
            status = 'failed'

        return GatewayResponse(
            ok=status not in {'failed', 'error', 'cancelled', 'expired'},
            status=status,
            message=payload.get('message') or 'Webhook received.',
            payload=payload,
            gateway_reference=self._extract_reference(payload),
        )

    def verify_webhook(self, raw_body, headers):
        timestamp = headers.get(self.config['WEBHOOK_TIMESTAMP_HEADER'])
        signature = headers.get(self.config['WEBHOOK_SIGNATURE_HEADER'])
        verification_token = headers.get(self.config['WEBHOOK_TOKEN_HEADER'])

        public_key = self.config.get('WEBHOOK_PUBLIC_KEY')
        if public_key and signature:
            if not timestamp:
                raise WebhookVerificationError("Missing webhook timestamp.")
            self._validate_timestamp(timestamp)
            self._verify_rsa_signature(raw_body, signature, public_key)
            return True

        expected_token = self.config.get('WEBHOOK_TOKEN')
        if expected_token:
            if not timestamp:
                raise WebhookVerificationError("Missing webhook timestamp.")
            self._validate_timestamp(timestamp)
            if not verification_token or not hmac.compare_digest(verification_token, expected_token):
                raise WebhookVerificationError("Webhook token mismatch.")
            return True

        raise WebhookVerificationError("Webhook verification is not configured.")

    def generate_checksum(self, payload):
        checksum_secret = self.config.get('CHECKSUM_SECRET')
        if not checksum_secret:
            return ''
        canonical = json.dumps(payload, separators=(',', ':'), sort_keys=True)
        digest = hashlib.sha256(f"{canonical}{checksum_secret}".encode('utf-8')).hexdigest()
        return digest

    def callback_digest(self, raw_body):
        return hashlib.sha256(raw_body).hexdigest()

    def _validate_timestamp(self, timestamp):
        try:
            callback_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        except ValueError as exc:
            raise WebhookVerificationError("Invalid webhook timestamp.") from exc

        now = timezone.now()
        if callback_time.tzinfo is None:
            callback_time = timezone.make_aware(callback_time, dt_timezone.utc)

        if abs(now - callback_time) > timedelta(seconds=self.config['WEBHOOK_MAX_AGE_SECONDS']):
            raise WebhookVerificationError("Expired webhook timestamp.")

    def _verify_rsa_signature(self, raw_body, signature, public_key_pem):
        try:
            from cryptography.exceptions import InvalidSignature
            from cryptography.hazmat.primitives import hashes, serialization
            from cryptography.hazmat.primitives.asymmetric import padding
        except ImportError as exc:
            raise WebhookVerificationError(
                "Install the 'cryptography' package to verify AzamPay webhook signatures."
            ) from exc

        try:
            public_key = serialization.load_pem_public_key(public_key_pem.encode('utf-8'))
            decoded_signature = base64.b64decode(signature)
            public_key.verify(decoded_signature, raw_body, padding.PKCS1v15(), hashes.SHA256())
        except (ValueError, InvalidSignature) as exc:
            raise WebhookVerificationError("Invalid webhook signature.") from exc

    def _post_json(self, url, payload, headers, timeout=None):
        timeout = timeout or self.timeout
        if HTTPX_AVAILABLE:
            return self._post_json_httpx(url, payload, headers, timeout)

        import time
        max_retries = 3

        headers_copy = dict(headers) if headers else {}
        if 'User-Agent' not in headers_copy:
            headers_copy['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        body = json.dumps(payload).encode('utf-8')
        req = request.Request(url, data=body, headers=headers_copy, method='POST')
        
        for attempt in range(max_retries):
            try:
                with request.urlopen(req, timeout=timeout) as response:
                    raw_response = response.read().decode('utf-8') or '{}'
                    return json.loads(raw_response)
            except error.HTTPError as exc:
                raw_error = exc.read().decode('utf-8') if exc.fp else '{}'
                logger.exception(
                    "AzamPay HTTP error",
                    extra={
                        'url': url,
                        'status_code': exc.code,
                        'response': self._sanitize_payload(raw_error),
                    },
                )
                try:
                    error_payload = json.loads(raw_error)
                except json.JSONDecodeError:
                    error_payload = {'message': raw_error or 'Unknown AzamPay error.'}
                message = error_payload.get('message') or f"AzamPay responded with HTTP {exc.code}."
                if exc.code >= 500:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    raise RetryablePaymentServiceError(message) from exc
                raise PaymentServiceError(message) from exc
            except (error.URLError, TimeoutError, socket.timeout) as exc:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.exception("AzamPay network failure", extra={'url': url})
                raise RetryablePaymentServiceError("AzamPay is currently unreachable. Please try again shortly.") from exc
            except json.JSONDecodeError as exc:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.exception("AzamPay invalid JSON response", extra={'url': url})
                raise RetryablePaymentServiceError("AzamPay returned an invalid response.") from exc

    def _post_json_httpx(self, url, payload, headers, timeout):
        import httpx
        import time
        max_retries = 3

        headers_copy = dict(headers) if headers else {}
        if 'User-Agent' not in headers_copy:
            headers_copy['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'

        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=timeout) as client:
                    response = client.post(url, json=payload, headers=headers_copy)
                    response.raise_for_status()
                    return response.json()
            except httpx.HTTPStatusError as exc:
                logger.exception(
                    "AzamPay HTTP error",
                    extra={
                        'url': url,
                        'status_code': exc.response.status_code,
                        'response': self._sanitize_payload(exc.response.text),
                    },
                )
                try:
                    error_payload = exc.response.json()
                except ValueError:
                    error_payload = {'message': exc.response.text or 'Unknown AzamPay error.'}
                message = error_payload.get('message') or f"AzamPay responded with HTTP {exc.response.status_code}."
                if exc.response.status_code >= 500:
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)
                        continue
                    raise RetryablePaymentServiceError(message) from exc
                raise PaymentServiceError(message) from exc
            except httpx.TimeoutException as exc:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.exception("AzamPay timeout", extra={'url': url})
                raise RetryablePaymentServiceError("AzamPay took too long to respond. Please try again shortly.") from exc
            except httpx.RequestError as exc:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.exception("AzamPay network failure", extra={'url': url})
                raise RetryablePaymentServiceError("AzamPay is currently unreachable. Please try again shortly.") from exc
            except ValueError as exc:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
                logger.exception("AzamPay invalid JSON response", extra={'url': url})
                raise RetryablePaymentServiceError("AzamPay returned an invalid response.") from exc

    def _extract_status(self, payload):
        data = payload.get('data') or {}
        properties = data.get('properties') or {}
        candidates = [
            payload.get('status'),
            payload.get('transactionStatus'),
            payload.get('transactionstatus'),
            payload.get('reference'),
            payload.get('transactionId'),
            payload.get('transid'),
            data.get('status'),
            properties.get('status'),
            properties.get('transactionStatus'),
            properties.get('transactionstatus'),
        ]
        for candidate in candidates:
            if not candidate:
                continue
            normalized = str(candidate).strip().lower()
            if normalized in {'successful', 'success', 'completed', 'complete'}:
                return 'success'
            if normalized in {'pending', 'processing', 'created', 'initiated'}:
                return 'pending'
            if normalized in {'retrying'}:
                return 'retrying'
            if normalized in {'failed', 'error', 'rejected'}:
                return 'failed'
            if normalized in {'cancelled', 'canceled'}:
                return 'cancelled'
            if normalized in {'expired'}:
                return 'expired'
        return None

    def _extract_reference(self, payload):
        data = payload.get('data') or {}
        properties = data.get('properties') or {}
        for candidate in (
            payload.get('reference'),
            payload.get('transactionId'),
            payload.get('transid'),
            payload.get('utilityref'),
            data.get('reference'),
            data.get('transactionId'),
            properties.get('reference'),
            properties.get('transactionId'),
            properties.get('referenceId'),
            properties.get('utilityref'),
        ):
            if candidate:
                return str(candidate)
        return ''

    def _sanitize_payload(self, payload):
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                return '[redacted-raw-response]'
        if isinstance(payload, list):
            return [self._sanitize_payload(item) for item in payload]
        if not isinstance(payload, dict):
            return payload

        redacted = {}
        sensitive_keys = {
            'accessToken', 'token', 'authorization', 'clientSecret', 'clientId',
            'appName', 'signature', 'checksum', 'accountNumber', 'phone_number',
            'phoneNumber', 'donorEmail', 'email',
        }
        for key, value in payload.items():
            if key in sensitive_keys:
                redacted[key] = '[redacted]'
            else:
                redacted[key] = self._sanitize_payload(value)
        return redacted

    def _extract_token_ttl(self, payload):
        data = payload.get('data') or {}
        candidates = (
            payload.get('expiresIn'),
            payload.get('expires_in'),
            data.get('expiresIn'),
            data.get('expires_in'),
        )
        for candidate in candidates:
            try:
                if candidate is not None:
                    return int(candidate)
            except (TypeError, ValueError):
                continue
        return self.config['TOKEN_CACHE_TTL']
