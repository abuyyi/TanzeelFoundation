"""
WSGI config for tanzeel project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""


import os
# Ensure .env variables are loaded
try:
	import dotenv
	dotenv.load_dotenv()
except ImportError:
	pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tanzeel.settings")

application = get_wsgi_application()
