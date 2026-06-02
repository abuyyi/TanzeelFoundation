
from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('coming-soon/', views.coming_soon, name='coming_soon'),
]
