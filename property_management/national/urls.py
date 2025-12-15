# national/urls.py
from django.urls import path
from . import views

app_name = 'national'

urlpatterns = [
    # Your existing URLs
    path('', views.district_list, name='district_list'),
    path('district/<str:dcode>/locals/', views.local_list, name='local_list'),
    path('district/<str:dcode>/summary/', views.district_summary, name='district_summary'),
    path('local/<int:local_id>/reports/', views.report_list, name='report_list'),
    path('report/<int:report_id>/', views.report_detail, name='report_detail'),
    path('upload/', views.upload_file, name='upload'),
    path('report/<int:report_id>/pdf/', views.report_print_pdf, name='report_print_pdf'),
    
    # ============================================
    # NEW URLs for Year-Over-Year Tracking
    # ============================================
    
    # 1. Report Creation with Copy Option
    path('local/<int:local_id>/report/create/', views.create_report, name='create_report'),
    
    # 2. Copy Report to Next Year
    path('report/<int:report_id>/copy/', views.copy_report, name='copy_report'),
    
    # 3. Building Management URLs
    path('report/<int:report_id>/pastoral-house/add/', views.add_pastoral_house, name='add_pastoral_house'),
    path('report/<int:report_id>/pastoral-house/<int:building_id>/edit/', views.edit_pastoral_house, name='edit_pastoral_house'),
    
    path('report/<int:report_id>/office/add/', views.add_office_building, name='add_office_building'),
    path('report/<int:report_id>/office/<int:building_id>/edit/', views.edit_office_building, name='edit_office_building'),
    
    path('report/<int:report_id>/other-building/add/', views.add_other_building, name='add_other_building'),
    path('report/<int:report_id>/other-building/<int:building_id>/edit/', views.edit_other_building, name='edit_other_building'),
    
    # 4. Bulk Operations
    path('report/<int:report_id>/buildings/bulk-add/', views.bulk_add_buildings, name='bulk_add_buildings'),
    path('report/<int:report_id>/copy-buildings/', views.copy_buildings_from_previous, name='copy_buildings'),
    
    # 5. Chapel Management (for consistency)
    path('report/<int:report_id>/chapel/add/', views.add_chapel, name='add_chapel'),
    path('report/<int:report_id>/chapel/<int:chapel_id>/edit/', views.edit_chapel, name='edit_chapel'),
]