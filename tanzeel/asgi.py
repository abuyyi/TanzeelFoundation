"""
ASGI config for tanzeel project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""


import os
# Ensure .env variables are loaded
try:
	import dotenv
	dotenv.load_dotenv()
except ImportError:
	pass

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tanzeel.settings")

application = get_asgi_application()
