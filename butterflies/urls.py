
# urls.py
# Defines URL patterns for the butterflies app.
# Maps URLs to view functions and class-based views for butterfly collections and traps.


from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Main list view for all collections and traps (custom view)
    path('', views.all_list, name='all_list'),
    # Form to add a new butterfly collection
    path('butterflies/add/', views.create_butterfly, name='create_butterfly'),
    # Form to add a new trap
    path('traps/add/', views.create_trap, name='create_trap'),

    # Generic dynamic list view for any model
    path('list/<str:model_name>/', views.dynamic_list, name='dynamic_list'),

    # Generic create/edit for any model
    path('add/<str:model_name>/', views.dynamic_create_edit, name='dynamic_create'),
    path('edit/<str:model_name>/<str:object_id>/', views.dynamic_create_edit, name='dynamic_edit'),

    # Generic detail and delete for any model
    path('detail/<str:model_name>/<str:object_id>/', views.dynamic_detail, name='dynamic_detail'),
    path('delete/<str:model_name>/<str:object_id>/', views.dynamic_delete, name='dynamic_delete'),

    # Test butterflyID detail view
    path('butterflyid/<str:butterflyid>/', views.butterflyid_detail, name='butterflyid_detail'),
]

# Serve static files in development (for admin CSS/JS)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
