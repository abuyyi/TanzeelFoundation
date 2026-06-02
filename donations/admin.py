from django.contrib import admin
from .models import Donation, PaymentTransaction, AzamPayWebhookEvent

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'created_at' , 'giving_frequency', 'payment_method', 'donation_type', 'amount', 'status')
    search_fields = ('first_name', 'last_name', 'email', 'payment_method')
    list_filter = ('status', 'donation_type', 'created_at')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ('external_id', 'status', 'amount', 'currency', 'created_at')
    search_fields = ('external_id', 'phone_number')
    list_filter = ('status', 'provider', 'created_at')

@admin.register(AzamPayWebhookEvent)
class AzamPayWebhookEventAdmin(admin.ModelAdmin):
    list_display = ('event_hash', 'verification_passed', 'processed', 'received_at')
    search_fields = ('event_hash', 'external_id')
    list_filter = ('verification_passed', 'processed', 'received_at')
