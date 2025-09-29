# auth_utils.py
# Custom authentication and authorization utilities for the butterflies app

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from functools import wraps

def is_guest_mode(request):
    """
    Check if the user is in guest mode (session flag set).
    """
    return request.session.get('guest_mode', False)

def guest_allowed(view_func):
    """
    Decorator to allow guest access to read-only views.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Allow if user is authenticated or in guest mode
        if request.user.is_authenticated or is_guest_mode(request):
            return view_func(request, *args, **kwargs)
        
        # If not authenticated and not guest, redirect to login page
        login_url = settings.LOGIN_URL
        return redirect(f"{login_url}?next={request.path}")
    
    return _wrapped_view

def admin_required(view_func):
    """
    Decorator to check if user has admin privileges (is_superuser or in 'Admin' group).
    Guest users are not allowed for admin-required views.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Guest mode is not allowed for admin operations
        if is_guest_mode(request):
            return render(request, 'butterflies/auth/access_denied.html', {
                'message': 'Guest users cannot perform administrative operations. Please log in with an admin account.'
            })
        
        # Superusers always have access
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        
        # Check if user is in Admin group
        if request.user.groups.filter(name='Admin').exists():
            return view_func(request, *args, **kwargs)
        
        # If not authenticated, redirect to login
        if not request.user.is_authenticated:
            login_url = settings.LOGIN_URL
            # Add the 'next' parameter to redirect back after login
            return redirect(f"{login_url}?next={request.path}")
            
        # If authenticated but no permission, show access denied
        return render(request, 'butterflies/auth/access_denied.html')
    
    return _wrapped_view
