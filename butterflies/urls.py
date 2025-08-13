# urls.py
# Defines URL patterns for the butterflies app.
# Maps URLs to consolidated view functions using the organized form approach.

from django.urls import path
from . import views

urlpatterns = [
    # Main list view for all collections and traps (custom view)
    path('', views.report_table, name='report_table'),
    path('<str:model_name>/all/', views.dynamic_list, name='dynamic_list'),
    # Form to add a new specimen (using organized form)
    path('specimen/add/', views.create_specimen, name='create_specimen'),
    # Form to add a new locality
    path('locality/add/', views.create_locality, name='create_locality'),
    # Form to add new initials
    path('initials/add/', views.create_initials, name='create_initials'),
    
    # Keep this URL for backward compatibility (redirects to the main specimen form)
    path('specimen/add/organized/', views.create_specimen, name='create_specimen_organized'),

    # Report table exports (specific routes first)
    path('report/export/csv/', views.export_report_csv, name='export_report_csv'),
    path('report/export/excel/', views.export_report_excel, name='export_report_excel'),
    
    # Generic model export/import
    path('<str:model_name>/export/csv/', views.export_model_csv, name='export_model_csv'),
    path('<str:model_name>/export/excel/', views.export_model_excel, name='export_model_excel'),
    path('<str:model_name>/import/', views.import_model, name='import_model'),
    
    # Generic dynamic list view for any model
    path('list/<str:model_name>/', views.dynamic_list, name='dynamic_list'),

    # Generic create/edit for any model (all using organized approach)
    path('add/<str:model_name>/', views.dynamic_create_edit, name='dynamic_create'),
    path('edit/<str:model_name>/<str:object_id>/', views.dynamic_create_edit, name='dynamic_edit'),
    
    # Keep these URLs for backward compatibility (redirect to the main routes)
    path('add/organized/<str:model_name>/', views.dynamic_create_edit, name='dynamic_create_organized'),
    path('edit/organized/<str:model_name>/<str:object_id>/', views.dynamic_create_edit, name='dynamic_edit_organized'),

    # Generic detail and delete for any model
    path('detail/<str:model_name>/<str:object_id>/', views.dynamic_detail, name='dynamic_detail'),
    path('delete/<str:model_name>/<str:object_id>/', views.dynamic_delete, name='dynamic_delete'),
    
    # Debug bulk delete for specimen table
    path('specimen/debug-bulk-delete/', views.debug_bulk_delete_specimen, name='debug_bulk_delete_specimen'),
]
