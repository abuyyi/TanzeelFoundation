import json
import logging
import re

import os

from django.shortcuts import render

def coming_soon(request):
    """Display the coming soon page"""
    return render(request, 'core/coming_soon.html')



import os
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import uuid
import requests


@csrf_exempt

def handler404(request, exception):
    return render(request, 'core/404.html', status=404)

def handler500(request):
    return render(request, 'core/500.html', status=500)
