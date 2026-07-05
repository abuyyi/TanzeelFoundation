from django.db import models

# Create your models here.
import uuid

from django.db import models


class Donation(models.Model):
    TITLE_CHOICES = [
        ('Mr', 'Mr'),
        ('Mrs', 'Mrs'),
        ('Miss', 'Miss'),
    ]

    DONATION_TYPE_CHOICES = [
        ('General Fund', 'General Fund'),
        ('Qurban', 'Qurban'),
        ('FundProject', 'FundProject'),
        ('Sadakah', 'Sadakah'),
    ]

    COUNTRY_CHOICES = [
        ('Most in Need', 'Most in Need'),
        ('Gaza', 'Zanzibar'),
        ('Syria', 'Dar es salaam'),
        ('Tanzania', 'Morogoro'),
    ]

    PROVIDE_CHOICES = [
        ('Social Service', 'Social Service'),
        ('Education Center', 'Education Center'),
        ('Waqfu', 'Waqfu'),
        ('TSDF', 'TSDF'),
    ]

    title = models.CharField(max_length=10, choices=TITLE_CHOICES)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=15)
    is_organization = models.BooleanField(default=False)
    country = models.CharField(max_length=50, choices=COUNTRY_CHOICES, blank=True, default='')
    postcode = models.CharField(max_length=20, blank=True, default='')
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    in_country = models.CharField(max_length=50, choices=COUNTRY_CHOICES)
    to_provide = models.CharField(max_length=50, choices=PROVIDE_CHOICES)
    age_confirmation = models.BooleanField(default=False)
    contact_email = models.BooleanField(default=False)
    contact_sms = models.BooleanField(default=False)
    contact_whatsapp = models.BooleanField(default=False)
    contact_post = models.BooleanField(default=False)
    gift_aid = models.BooleanField(default=False)
    card_number = models.CharField(max_length=16, blank=True, default='')
    expiry_date = models.CharField(max_length=5, blank=True, default='')
    security_code = models.CharField(max_length=4, blank=True, default='')
    agree_to_terms = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    GIVING_FREQUENCY_CHOICES = [
        ('one-off', 'One-off'),
        ('every-day', 'Every Day'),
        ('every-friday', 'Every Friday'),
        ('every-month', 'Every Month'),
    ]

    giving_frequency = models.CharField(
        max_length=20,
        choices=GIVING_FREQUENCY_CHOICES,
        default='one-off',
    )
    payment_method = models.CharField(max_length=20, default='mobile')
    DONATION_STATUS_PENDING = 'pending'
    DONATION_STATUS_COMPLETED = 'completed'
    DONATION_STATUS_FAILED = 'failed'
    DONATION_STATUS_CANCELLED = 'cancelled'
    DONATION_STATUS_EXPIRED = 'expired'

    DONATION_STATUS_CHOICES = [
        (DONATION_STATUS_PENDING, 'Pending'),
        (DONATION_STATUS_COMPLETED, 'Completed'),
        (DONATION_STATUS_FAILED, 'Failed'),
        (DONATION_STATUS_CANCELLED, 'Cancelled'),
        (DONATION_STATUS_EXPIRED, 'Expired'),
    ]

    status = models.CharField(
        max_length=20,
        choices=DONATION_STATUS_CHOICES,
        default=DONATION_STATUS_PENDING,
    )
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Donation by {self.first_name} {self.last_name} - GBP {self.amount}"


class PaymentTransaction(models.Model):
    STATUS_CREATED = 'created'
    STATUS_INITIATED = 'initiated'
    STATUS_PENDING = 'pending'
    STATUS_RETRYING = 'retrying'
    STATUS_PROCESSING = 'processing'
    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_EXPIRED = 'expired'
    STATUS_ERROR = 'error'

    STATUS_CHOICES = [
        (STATUS_CREATED, 'Created'),
        (STATUS_INITIATED, 'Initiated'),
        (STATUS_PENDING, 'Pending'),
        (STATUS_RETRYING, 'Retrying'),
        (STATUS_PROCESSING, 'Processing'),
        (STATUS_SUCCESS, 'Success'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_EXPIRED, 'Expired'),
        (STATUS_ERROR, 'Error'),
    ]

    FINAL_STATUSES = {
        STATUS_SUCCESS,
        STATUS_FAILED,
        STATUS_CANCELLED,
        STATUS_EXPIRED,
        STATUS_ERROR,
    }

    @property
    def is_final(self):
        return self.status in self.FINAL_STATUSES

    donation = models.ForeignKey(Donation, on_delete=models.CASCADE, related_name='transactions')
    external_id = models.CharField(max_length=64, unique=True, db_index=True)
    idempotency_key = models.CharField(max_length=64, unique=True)
    provider = models.CharField(max_length=32)
    phone_number = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=8, default='TZS')
    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_CREATED, db_index=True)
    gateway_reference = models.CharField(max_length=128, blank=True, default='', db_index=True)
    gateway_status = models.CharField(max_length=64, blank=True, default='')
    gateway_message = models.TextField(blank=True, default='')
    callback_hash = models.CharField(max_length=64, blank=True, default='')
    callback_verified_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    initiation_attempts = models.PositiveIntegerField(default=0)
    last_initiation_at = models.DateTimeField(null=True, blank=True)
    next_retry_at = models.DateTimeField(null=True, blank=True)
    last_error_at = models.DateTimeField(null=True, blank=True)
    request_payload = models.JSONField(default=dict, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    callback_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @staticmethod
    def new_external_id():
        return uuid.uuid4().hex

    def __str__(self):
        return f"{self.external_id} - {self.status}"


class AzamPayWebhookEvent(models.Model):
    event_hash = models.CharField(max_length=64, db_index=True)
    external_id = models.CharField(max_length=64, blank=True, default='', db_index=True)
    gateway_reference = models.CharField(max_length=128, blank=True, default='', db_index=True)
    headers = models.JSONField(default=dict, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    verification_passed = models.BooleanField(default=False)
    duplicate = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    processing_note = models.CharField(max_length=255, blank=True, default='')
    transaction = models.ForeignKey(
        PaymentTransaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='webhook_events',
    )
    received_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event_hash} - {self.processing_note or 'received'}"
