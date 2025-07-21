
"""
asgi.py
ASGI config for research_data_app project.
This file sets up the ASGI application for asynchronous web servers and deployment.

Main functionality:
    - Sets the default settings module for the project.
    - Exposes the ASGI application callable for use by ASGI servers.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_data_app.settings')

application = get_asgi_application()
