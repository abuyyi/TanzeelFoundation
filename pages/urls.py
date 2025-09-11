from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.homepage, name='homepage'),
]
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'