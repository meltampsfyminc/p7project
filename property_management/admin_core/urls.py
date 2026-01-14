from django.urls import path
from . import views

app_name = "admin_core"

urlpatterns = [
    path("workers/bulk-add/", views.worker_bulk_create, name="worker_bulk_add"),
    path("workers/", views.worker_list, name="worker_list"),
    path("", views.admin_dashboard, name="dashboard"),
# Departments
    path("departments/", views.department_list, name="department_list"),
    path("departments/add/", views.department_create, name="department_add"),
    path("departments/<int:pk>/edit/", views.department_update, name="department_edit"),
    path("departments/<int:pk>/delete/", views.department_delete, name="department_delete"),
    # Mass encoding
    path("departments/bulk-add/", views.department_bulk_create, name="department_bulk_add"),
    
    
    
    path("offices/", views.office_list, name="office_list"),
    path("offices/add/", views.office_create, name="office_create"),
    path("offices/<int:pk>/edit/", views.office_update, name="office_update"),
    path("workers/", views.worker_list, name="worker_list"),
    path("workers/add/", views.worker_create, name="worker_create"),
    path("workers/<int:pk>/edit/", views.worker_update, name="worker_update"),
    path("workers/<int:pk>/detail/", views.worker_detail, name="worker_detail"),
    path("worker-offices/", views.worker_office_list, name="worker_office_list"),
    path("worker-offices/add/", views.worker_office_create, name="worker_office_create"),
    path("worker-offices/<int:pk>/edit/", views.worker_office_update, name="worker_office_update"),
    path("housing-assignments/", views.housing_assignment_list, name="housing_assignment_list"),
    path("housing-assignments/add/", views.housing_assignment_create, name="housing_assignment_create"),
    path("housing-assignments/<int:pk>/edit/", views.housing_assignment_update, name="housing_assignment_update"),
    path("mass/departments/", views.mass_departments, name="mass_departments"),
    path("mass/sections/", views.mass_sections, name="mass_sections"),
    path("mass/workers/", views.mass_workers, name="mass_workers"),
    path("mass/offices/", views.mass_offices, name="mass_offices"),
    
    # Sections
    path("sections/", views.section_list, name="section_list"),
    path("sections/add/", views.section_create, name="section_add"),
    path("sections/<int:pk>/edit/", views.section_update, name="section_edit"),
    path("sections/<int:pk>/delete/", views.section_delete, name="section_delete"),
    path("sections/bulk-add/", views.section_bulk_create, name="section_bulk_add"),

# Admin Buildings
    path("buildings/", views.admin_building_list, name="admin_building_list"),
    path("buildings/add/", views.admin_building_create, name="admin_building_add"),
    path("buildings/<int:pk>/edit/", views.admin_building_update, name="admin_building_edit"),
    path("buildings/<int:pk>/delete/", views.admin_building_delete, name="admin_building_delete"),
    path("buildings/bulk-add/", views.admin_building_bulk_create, name="admin_building_bulk_add"),
]
