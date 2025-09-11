from django.contrib import admin
from .models import SiteSettings

class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('foundation_name', 'contact_email')
    fieldsets = (
        ('Basic Information', {
            'fields': ('foundation_name', 'contact_email', 'contact_phone', 'address')
        }),
        ('Social Media', {
            'fields': ('facebook_url', 'twitter_url', 'instagram_url', 'linkedin_url', 'youtube_url')
        }),
        ('Content', {
            'fields': ('mission_statement', 'vision_statement', 'about_us')
        }),
        ('Media', {
            'fields': ('logo', 'favicon')
        }),
    )
admin.site.register(SiteSettings, SiteSettingsAdmin)

