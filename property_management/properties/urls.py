from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # Authentication URLs
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('setup-2fa/', views.setup_2fa, name='setup_2fa'),
    path('backup-codes/', views.view_backup_codes, name='view_backup_codes'),
    
    # Property management URLs
    path('properties/', views.property_list, name='property_list'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('upload/', views.upload_file, name='upload_file'),
    path('import-history/', views.import_history, name='import_history'),
    path('housing-unit/<int:pk>/', views.housing_unit_detail, name='housing_unit_detail'),
    path('building/<int:property_id>/', views.building_occupants, name='building_occupants'),
    
    # Item Transfer URLs
    path('transfers/', views.transfer_list, name='transfer_list'),
    path('transfers/create/', views.transfer_create, name='transfer_create'),
    path('transfers/<int:pk>/', views.transfer_detail, name='transfer_detail'),
    path('transfers/history/', views.transfer_history, name='transfer_history'),
]
