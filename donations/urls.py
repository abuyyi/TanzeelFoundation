"""
URL configuration for donation_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'donations'

urlpatterns = [
    #path('', views.donation_page, name='donation_page'),  # Set donation_page as the default homepage
    path('donate/', views.donation_page, name='donation_page'),
    path('payments/azampay/webhook/', views.azampay_webhook, name='azampay_webhook'),
    path('payments/<str:external_id>/', views.payment_status, name='payment_status'),
    path('payments/<str:external_id>/status/', views.payment_status_api, name='payment_status_api'),
    path('payments/<str:external_id>/recover/', views.payment_recover, name='payment_recover'),
    path(
        'qurban/',
        views.donation_page,
        {
            'fixed_donation_type': 'Qurban',
            'page_heading': 'Qurban Donation',
            'page_subheading': 'The Qurban project, a charitable initiative, successfully provided vital support to cover 1,200 families accross the Dar es salaam region. Through the generous contributions of our donors, we were able to distribute meat to those in need, ensuring that these families had access to nutritious food during a sacred period of Eid a-Adha.',
            'page_breadcrumb': 'Qurban',
            'banner_heading': 'Qurban',
            'banner_description': 'Give Qurban securely and make a meaningful impact through our established donation workflow.',
            'template_name': 'qurban.html',
        },
        name='qurban',
    ),
    path(
        'tsdf/',
        RedirectView.as_view(pattern_name='donations:qurban', permanent=True),
        name='tsdf',
    ),
    path(
        'sadaka/',
        views.donation_page,
        {
            'fixed_donation_type': 'Sadakah',
            'page_heading': 'Sadakah',
            'page_subheading': 'Sadaka,an act of voluntary charity in islam, provides vital assistance to those in need, offering hope and support for a brighter future within communities facing hardship. For our own success, we should spend time, money and efforts in giving sadaka for the pleasure of Allah as the rewards of sadaka is nothing but success, especially in Hereafter.',
            'page_breadcrumb': 'Sadakah',
            'banner_heading': 'Donate to Tanzeel Foundation',
            'banner_description': '100% of Your generous donations help us provide essential services to those in need.',
        },
        name='sadaka',
    ),
    path(
        'fund_project/',
        views.donation_page,
        {
            'fixed_donation_type': 'FundProject',
            'page_heading': 'Fund Project',
            'page_subheading': 'Your donation helps us develop and sustain impactful projects that improve lives and strengthen communities. Every contribution supports initiatives in education, social welfare, community development, infrastructure, and other charitable programs. Together, we can create lasting positive change and build a brighter future for those in need.',
            'page_breadcrumb': 'Fund Project',
            'banner_heading': 'Fund Project',
            'banner_description': '100% of your generous donations help us in funding our short and long run projects.',
        },
        name='fund_project',
    ),
]
