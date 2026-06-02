import json
from datetime import datetime, timezone

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test.client import RequestFactory
from django.urls import reverse

from donations.models import PaymentTransaction
from donations.services.payment_service import AzamPayService
from donations.views import azampay_webhook


class Command(BaseCommand):
    help = "Simulate an AzamPay webhook callback for a PaymentTransaction."

    def add_arguments(self, parser):
        parser.add_argument(
            'external_id',
            type=str,
            help='The PaymentTransaction external_id to target.',
        )
        parser.add_argument(
            '--status',
            choices=['success', 'pending', 'failed', 'cancelled', 'expired', 'error'],
            default='success',
            help='The webhook status to simulate.',
        )
        parser.add_argument(
            '--message',
            type=str,
            default='',
            help='Optional webhook message text.',
        )

    def handle(self, *args, **options):
        external_id = options['external_id']
        status = options['status']
        message = options['message'] or f'Simulated {status} webhook event.'

        transaction = PaymentTransaction.objects.select_related('donation').filter(external_id=external_id).first()
        if not transaction:
            raise CommandError(f'No PaymentTransaction found for external_id={external_id}')

        payload = {
            'externalId': transaction.external_id,
            'reference': transaction.gateway_reference or f'mock-{transaction.external_id}',
            'status': status,
            'message': message,
            'data': {
                'externalId': transaction.external_id,
                'reference': transaction.gateway_reference or f'mock-{transaction.external_id}',
                'status': status,
            },
        }

        timestamp = datetime.now(timezone.utc).isoformat()
        headers = {
            'HTTP_X_AZAMPAY_TIMESTAMP': timestamp,
        }
        webhook_token = settings.AZAMPAY.get('WEBHOOK_TOKEN')
        if webhook_token:
            headers['HTTP_X_AZAMPAY_WEBHOOK_TOKEN'] = webhook_token
        else:
            self.stderr.write('Warning: AZAMPAY_WEBHOOK_TOKEN is not configured; verification may fail.')

        request = RequestFactory().post(
            reverse('donations:azampay_webhook'),
            data=json.dumps(payload),
            content_type='application/json',
            **headers,
        )

        response = azampay_webhook(request)
        self.stdout.write(f'Response status: {response.status_code}')
        if hasattr(response, 'content'):
            self.stdout.write(response.content.decode('utf-8'))
