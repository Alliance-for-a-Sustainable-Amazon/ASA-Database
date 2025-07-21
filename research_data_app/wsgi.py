
"""
wsgi.py
WSGI config for research_data_app project.
This file sets up the WSGI application for synchronous web servers and deployment.

Main functionality:
    - Sets the default settings module for the project.
    - Exposes the WSGI application callable for use by WSGI servers.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_data_app.settings')

application = get_wsgi_application()
