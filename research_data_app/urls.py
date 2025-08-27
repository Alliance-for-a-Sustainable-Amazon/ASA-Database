
"""
urls.py
URL configuration for research_data_app project.
Defines the main URL patterns for the project, including admin and app-specific routes.

Patterns:
    - 'admin/': Django admin site.
    - 'accounts/': Authentication-related views
    - '': Includes all URLs from the butterflies app.
"""


from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Authentication paths
    path('accounts/login/', auth_views.LoginView.as_view(template_name='butterflies/auth/login.html'), name='login'),
    # path('', RedirectView.as_view(url='/butterflies/', permanent=False)),
    path('', include('butterflies.urls')),
    path('i18n/', include('django.conf.urls.i18n')),
]
