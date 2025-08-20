# urls.py
# Defines URL patterns for the butterflies app.
# Maps URLs to consolidated view functions using the organized form approach.

from django.urls import path
from . import views
from . import views_user_management

urlpatterns = [
    # Dashboard and main views
    path('', views.report_table, name='report_table'),
    
    # Model-specific creation routes
    path('specimen/add/', views.create_specimen, name='create_specimen'),
    path('locality/add/', views.create_locality, name='create_locality'),
    path('initials/add/', views.create_initials, name='create_initials'),
    
    # List views
    path('<str:model_name>/all/', views.dynamic_list, name='dynamic_list'),
    path('list/<str:model_name>/', views.dynamic_list, name='dynamic_list'),

    # Export/import routes
    path('report/export/csv/', views.export_report_csv, name='export_report_csv'),
    path('report/export/excel/', views.export_report_excel, name='export_report_excel'),
    path('<str:model_name>/export/csv/', views.export_model_csv, name='export_model_csv'),
    path('<str:model_name>/export/excel/', views.export_model_excel, name='export_model_excel'),
    path('<str:model_name>/import/', views.import_model, name='import_model'),
    
    # Generic CRUD operations for dynamic models
    path('add/<str:model_name>/', views.dynamic_create_edit, name='dynamic_create'),
    path('edit/<str:model_name>/<str:object_id>/', views.dynamic_create_edit, name='dynamic_edit'),
    path('detail/<str:model_name>/<str:object_id>/', views.dynamic_detail, name='dynamic_detail'),
    path('delete/<str:model_name>/<str:object_id>/', views.dynamic_delete, name='dynamic_delete'),
    
    # Debug and utility routes
    path('specimen/debug-bulk-delete/', views.debug_bulk_delete_specimen, name='debug_bulk_delete_specimen'),
    
    # Authentication routes
    path('accounts/logout/', views.custom_logout, name='custom_logout'),
    
    # User management routes
    path('users/', views_user_management.UserListView.as_view(), name='user_list'),
    path('users/add/', views_user_management.UserCreateView.as_view(), name='user_create'),
    path('users/<int:pk>/edit/', views_user_management.UserUpdateView.as_view(), name='user_edit'),
    path('users/<int:pk>/delete/', views_user_management.UserDeleteView.as_view(), name='user_delete'),
]
