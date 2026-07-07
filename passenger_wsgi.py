"""
Passenger entry point for cPanel ("Setup Python App").

cPanel's Passenger imports the module-level ``application`` callable from this
file. We simply reuse the project's WSGI application, which loads settings and
the .env file. Ensure the cPanel Python App's "Application startup file" is set
to `passenger_wsgi.py` and the "Application Entry point" to `application`.
"""

import os
import sys

# Make sure the project root is importable.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tanzeel.settings")

from tanzeel.wsgi import application  # noqa: E402  (import after sys.path setup)
