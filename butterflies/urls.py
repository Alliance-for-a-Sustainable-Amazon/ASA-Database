
# urls.py
# Defines URL patterns for the butterflies app.
# Maps URLs to view functions and class-based views for butterfly collections and traps.

from django.urls import path
from . import views

urlpatterns = [
    # Main list view for all collections and traps (custom view)
    path('', views.all_list, name='all_list'),
    # Form to add a new specimen
    path('specimen/add/', views.create_specimen, name='create_specimen'),
    # Form to add a new locality
    path('locality/add/', views.create_locality, name='create_locality'),
    # Form to add new initials
    path('initials/add/', views.create_initials, name='create_initials'),

    # Generic dynamic list view for any model
    path('list/<str:model_name>/', views.dynamic_list, name='dynamic_list'),

    # Generic create/edit for any model
    path('add/<str:model_name>/', views.dynamic_create_edit, name='dynamic_create'),
    path('edit/<str:model_name>/<str:object_id>/', views.dynamic_create_edit, name='dynamic_edit'),

    # Generic detail and delete for any model
    path('detail/<str:model_name>/<str:object_id>/', views.dynamic_detail, name='dynamic_detail'),
    path('delete/<str:model_name>/<str:object_id>/', views.dynamic_delete, name='dynamic_delete'),
]
