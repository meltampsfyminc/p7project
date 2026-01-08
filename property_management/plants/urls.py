from django.urls import path
from . import views

app_name = 'plants'

urlpatterns = [
    path('', views.plant_list, name='plant_list'),
    path('upload/', views.plant_upload, name='plant_upload'),
    path('create/', views.plant_create, name='plant_create'),
    path('<int:pk>/', views.plant_detail, name='plant_detail'),
    path('<int:pk>/update/', views.plant_update, name='plant_update'),
    path('<int:pk>/delete/', views.plant_delete, name='plant_delete'),
]
