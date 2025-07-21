
"""
urls.py
URL configuration for research_data_app project.
Defines the main URL patterns for the project, including admin and app-specific routes.

Patterns:
    - 'admin/': Django admin site.
    - '': Includes all URLs from the butterflies app.
"""


from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', RedirectView.as_view(url='/butterflies/', permanent=False)),
    path('', include('butterflies.urls')),
]
