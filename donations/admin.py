from datetime import date

from django.contrib import admin
from django.utils import timezone
from django.utils.html import escape, format_html
from .models import Donation, PaymentTransaction, AzamPayWebhookEvent

# Customize admin headers and titles
admin.site.site_header = "Tanzeel Foundation Admin"
admin.site.site_title = "Tanzeel Admin Portal"
admin.site.index_title = "Welcome to Tanzeel Foundation Admin Portal"


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
    change_list_template = 'admin/donations/azampaywebhookevent/change_list.html'
    list_display = ('event_card', 'verification_status', 'processing_status', 'received_at')
    list_display_links = ('event_card',)
    search_fields = ('event_hash', 'external_id', 'gateway_reference', 'processing_note')
    list_filter = ('verification_passed', 'processed', 'duplicate', 'received_at')
    ordering = ('-received_at',)
    list_per_page = 25
    readonly_fields = ('received_at',)

    def changelist_view(self, request, extra_context=None):
        queryset = self.get_queryset(request)
        now = timezone.now()
        extra_context = extra_context or {}
        extra_context.update({
            'stats_total': queryset.count(),
            'stats_success': queryset.filter(verification_passed=True, processed=True).count(),
            'stats_failed': queryset.filter(verification_passed=False, processed=False, duplicate=False).count(),
            'stats_pending': queryset.filter(processed=False, verification_passed=False).count(),
            'stats_today': queryset.filter(received_at__date=date.today()).count(),
            'stats_this_month': queryset.filter(received_at__month=now.month, received_at__year=now.year).count(),
        })
        return super().changelist_view(request, extra_context=extra_context)

    def event_card(self, obj):
        note = obj.processing_note or 'Awaiting processing'
        preview = obj.event_hash[:18] + ('…' if len(obj.event_hash) > 18 else '')
        return format_html(
            '<div class="webhook-event-card"><strong>{}</strong><span>{}</span></div>',
            escape(preview),
            escape(note),
        )

    event_card.short_description = 'Event'

    def verification_status(self, obj):
        label = 'Verified' if obj.verification_passed else 'Pending'
        badge_class = 'success' if obj.verification_passed else 'danger'
        return format_html('<span class="webhook-status-badge badge-{}">{}</span>', badge_class, label)

    verification_status.short_description = 'Verification'

    def processing_status(self, obj):
        if obj.processed:
            label = 'Processed'
            badge_class = 'success'
        elif obj.duplicate:
            label = 'Duplicate'
            badge_class = 'warning'
        else:
            label = 'Queued'
            badge_class = 'info'
        return format_html('<span class="webhook-status-badge badge-{}">{}</span>', badge_class, label)

    processing_status.short_description = 'Processing'
