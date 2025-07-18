from django.urls import path
from . import views

urlpatterns = [
    path('', views.all_list, name='all_list'),
    path('butterflies/add/', views.create_butterfly, name='create_butterfly'),
    path('traps/add/', views.create_trap, name='create_trap'),
    path('butterflies/', views.ButterflyListView.as_view(), name='butterfly_list'),
    path('traps/', views.TrapListView.as_view(), name='trap_list'),
]
