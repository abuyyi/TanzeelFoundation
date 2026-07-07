"""
URL configuration for tanzeel project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as serve_static

from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("core/", include("core.urls")),
    path("", include("pages.urls")),
    path("", include("donations.urls")),  # Add this line to include donation URLs

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
else:
    # In production WhiteNoise serves /static/. Serve user-uploaded /media/
    # through the app so images work regardless of how the web server maps
    # the document root. For higher traffic, offload /media/ to Apache via a
    # symlink into the web root (see DEPLOY.md) and this route becomes a fallback.
    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve_static,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]
