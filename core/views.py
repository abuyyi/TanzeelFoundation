from django.shortcuts import render
from django.http import Http404
from django.template import TemplateDoesNotExist

# Create your views here.

def handler404(request, exception):
    return render(request, 'core/404.html', status=404)

def handler500(request):
    return render(request, 'core/500.html', status=500)

def base(request):
    return render(request, 'base.html')
