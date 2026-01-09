"""
URL Configuration for property_management project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='properties/', permanent=False)),
    path('admin/', admin.site.urls),
    path('properties/', include('properties.urls')),
    path('gusali/', include('gusali.urls')),
    path('kagamitan/', include('kagamitan.urls')),
    path('lupa/', include('lupa.urls')),
    path('plants/', include('plants.urls')),
    path('vehicles/', include('vehicles.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    # Core
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Housing Units
    path('housing-unit/create/', views.housing_unit_create, name='housing_unit_create'),
    path('housing-unit/<int:pk>/', views.housing_unit_detail, name='housing_unit_detail'),
    path('housing-unit/<int:pk>/edit/', views.housing_unit_update, name='housing_unit_update'),
    path('housing-unit/<int:pk>/delete/', views.housing_unit_delete, name='housing_unit_delete'),

    # 🔥 Inventory CRUD
    path(
        'inventory/add/<int:housing_unit_pk>/',
        views.inventory_create,
        name='inventory_create'
    ),
    path(
        'inventory/<int:pk>/edit/',
        views.inventory_update,
        name='inventory_update'
    ),
    path(
        'inventory/<int:pk>/delete/',
        views.inventory_delete,
        name='inventory_delete'
    ),
]
