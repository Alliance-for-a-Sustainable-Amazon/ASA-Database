"""
settings_azure.py
Production settings for Azure App Service deployment.
This file extends the base settings and configures the Django project for production use on Azure.

Changes from base settings:
    - Uses environment variables for sensitive settings
    - Configures Azure PostgreSQL database connection
    - Sets up proper security settings for production
    - Configures static files for Azure
"""

import os
from .settings import *

# SECURITY: Use environment variables for sensitive settings
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', SECRET_KEY)
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'

# Allow Azure App Service domains
ALLOWED_HOSTS = [
    '.azurewebsites.net',
    'localhost',
    '127.0.0.1',
    '169.254.129.4',  # Azure internal IP address
    '169.254.131.4',  # Another Azure internal IP address
    '169.254.131.2',  # Additional Azure internal IP seen in logs
    '0.0.0.0',        # Generic bind address
]

# Add any custom domains here
custom_host = os.environ.get('WEBSITE_HOSTNAME')
if custom_host:
    ALLOWED_HOSTS.append(custom_host)
    
# Special handling for ALLOWED_HOSTS from environment variable
allowed_hosts_env = os.environ.get('ALLOWED_HOSTS', '')
if allowed_hosts_env:
    ALLOWED_HOSTS.extend([host.strip() for host in allowed_hosts_env.split(',')])

# Add any additional hosts from environment variables
additional_hosts = os.environ.get('ADDITIONAL_ALLOWED_HOSTS', '')
if additional_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in additional_hosts.split(',')])

# Enforce HTTPS
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Database: Use Azure PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DATABASE', ''),
        'USER': os.environ.get('POSTGRES_USER', ''),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
        'HOST': os.environ.get('POSTGRES_HOST', ''),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        }
    }
}

# Static files: Use Azure blob storage or the default filesystem
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add WhiteNoise for static files
] + MIDDLEWARE

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Enable WhiteNoise compression and caching
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging configuration for Azure
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}
