# auth_utils.py
# Custom authentication and authorization utilities for the butterflies app

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings
from functools import wraps

def admin_required(view_func):
    """
    Decorator to check if user has admin privileges (is_superuser or in 'Admin' group).
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
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
