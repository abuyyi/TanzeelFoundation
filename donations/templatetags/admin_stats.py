from django import template
from django.contrib.auth.models import User
from django.db.models import Sum
from donations.models import Donation, PaymentTransaction

register = template.Library()

@register.simple_tag
def get_total_users():
    try:
        return User.objects.count()
    except Exception:
        return 0

@register.simple_tag
def get_total_revenue():
    try:
        total = Donation.objects.filter(status='completed').aggregate(total=Sum('amount'))['total']
        return f"{float(total or 0):,.2f}"
    except Exception:
        return "0.00"

@register.simple_tag
def get_success_rate():
    try:
        total = PaymentTransaction.objects.count()
        if total == 0:
            return "100"
        successful = PaymentTransaction.objects.filter(status='success').count()
        return f"{int((successful / total) * 100)}"
    except Exception:
        return "100"

@register.simple_tag
def get_open_transactions():
    try:
        return PaymentTransaction.objects.exclude(status__in=[
            PaymentTransaction.STATUS_SUCCESS,
            PaymentTransaction.STATUS_FAILED,
            PaymentTransaction.STATUS_CANCELLED,
            PaymentTransaction.STATUS_EXPIRED,
            PaymentTransaction.STATUS_ERROR
        ]).count()
    except Exception:
        return 0

@register.simple_tag
def get_recent_transactions(limit=5):
    try:
        return PaymentTransaction.objects.select_related('donation').order_by('-created_at')[:limit]
    except Exception:
        return []

@register.simple_tag
def get_recent_donations(limit=5):
    try:
        return Donation.objects.order_by('-created_at')[:limit]
    except Exception:
        return []

@register.simple_tag
def get_latest_users(limit=5):
    try:
        return User.objects.order_by('-date_joined')[:limit]
    except Exception:
        return []
