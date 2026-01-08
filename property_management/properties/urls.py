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
    path('housing-unit/create/', views.housing_unit_create, name='housing_unit_create'),
    path('housing-unit/<int:pk>/update/', views.housing_unit_update, name='housing_unit_update'),
    path('housing-unit/<int:pk>/delete/', views.housing_unit_delete, name='housing_unit_delete'),
    path('building/<int:property_id>/', views.building_occupants, name='building_occupants'),
    path('building/<int:pk>/map/', views.building_map, name='building_map'),
    
    # Item Transfer URLs
    path('transfers/', views.transfer_list, name='transfer_list'),
    path('transfers/create/', views.transfer_create, name='transfer_create'),
    path('transfers/<int:pk>/', views.transfer_detail, name='transfer_detail'),
    path('transfers/history/', views.transfer_history, name='transfer_history'),

    # Search & Summary URLs
    path('search/district/', views.district_search, name='district_search'),
    path('district/<str:dcode>/', views.district_detail, name='district_detail'),
    path('local/<str:lcode>/summary/', views.local_summary, name='local_summary'),
    path('search/housing/', views.housing_search, name='housing_search'),
]
