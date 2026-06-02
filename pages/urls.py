from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('blog/', views.blog, name='blog'),
    path("terms/", views.terms_of_service, name="terms_of_service"),
    path("policy/", views.privacy_policy, name="privacy_policy"),
    path('appeals/', views.appeals, name='appeals'),
    path('appeals/<slug:slug>/', views.appeal_detail, name='appeal_detail'),
]
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'