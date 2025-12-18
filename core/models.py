from django.db import models

class SiteSettings(models.Model):
    foundation_name = models.CharField(max_length=255, default="Tanzeel Foundation")
    contact_email = models.EmailField(default="info@tanzeelfoundation.org")
    contact_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    mission_statement = models.TextField(blank=True)
    vision_statement = models.TextField(blank=True)
    about_us = models.TextField(blank=True)
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    favicon = models.ImageField(upload_to='favicons/', blank=True, null=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.foundation_name

# Donation model for simple payment integration
class Donation(models.Model):
    GIVING_FREQUENCY_CHOICES = [
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
        ("friday", "Every Friday"),
    ]
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("card", "Card"),
        ("mobile", "Mobile Pay"),
    ]

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donation_type = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    mobile_number = models.CharField(max_length=20)
    giving_frequency = models.CharField(max_length=20, choices=GIVING_FREQUENCY_CHOICES)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="PENDING")
    pesapal_transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.amount} ({self.status})"
