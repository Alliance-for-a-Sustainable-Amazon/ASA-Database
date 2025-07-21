#!/usr/bin/env python
"""
manage.py
Entry point for Django's command-line utility for administrative tasks.
This script allows you to interact with your Django project via the command line.
You can use it to run the development server, make migrations, migrate the database, create superusers, and more.

Main functionality:
    - Sets the default settings module for the Django project.
    - Imports and runs Django's execute_from_command_line to process commands.
    - Handles ImportError if Django is not installed or the virtual environment is not activated.
"""
import os
import sys


def main():
    """
    Run administrative tasks for the Django project.
    This function sets up the environment and delegates command-line arguments to Django's management system.
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'research_data_app.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
