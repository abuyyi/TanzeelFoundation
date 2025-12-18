
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('donate/', views.donation_view, name='donate'),
    path('pesapal-callback/', views.pesapal_callback, name='pesapal_callback'),
]
