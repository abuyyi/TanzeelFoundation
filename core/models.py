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
