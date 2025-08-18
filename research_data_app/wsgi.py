
"""
wsgi.py
WSGI config for research_data_app project.
This file sets up the WSGI application for synchronous web servers and deployment.

Main functionality:
    - Sets the default settings module for the project.
    - Exposes the WSGI application callable for use by WSGI servers.
"""

import os
import sys
from pathlib import Path

# Add the project path to the Python path so that we can import from the project
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Load environment variables from .env file, if present
try:
    from dotenv import load_dotenv
    env_path = BASE_DIR / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
except ImportError:
    pass

# Check for Azure-specific settings
settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', 'research_data_app.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
