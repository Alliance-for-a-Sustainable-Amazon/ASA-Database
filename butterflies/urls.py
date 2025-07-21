
# urls.py
# Defines URL patterns for the butterflies app.
# Maps URLs to view functions and class-based views for butterfly collections and traps.

from django.urls import path
from . import views

urlpatterns = [
    # Main list view for all collections and traps (custom view)
    path('', views.all_list, name='all_list'),
    # Form to add a new butterfly collection
    path('butterflies/add/', views.create_butterfly, name='create_butterfly'),
    # Form to add a new trap
    path('traps/add/', views.create_trap, name='create_trap'),
    # List view for butterfly collections
    path('butterflies/', views.ButterflyListView.as_view(), name='butterfly_list'),
    # List view for traps
    path('traps/', views.TrapListView.as_view(), name='trap_list'),
]
